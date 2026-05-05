import torch
import torch.nn as nn
import torch.nn.functional as F

class ResidualCNNBlock(nn.Module):

    def __init__(self, d_model=128):
        super().__init__()
        self.conv1 = nn.Conv2d(d_model, d_model, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(d_model, d_model, kernel_size=3, padding=1)
        self.norm1 = nn.BatchNorm2d(d_model)
        self.norm2 = nn.BatchNorm2d(d_model)

    def forward(self, x):
        residual = x
        x = F.gelu(self.norm1(self.conv1(x)))
        x = self.norm2(self.conv2(x))
        x = F.gelu(x + residual)
        return x
    
class ScrabbleDistillNet(nn.Module):
    def __init__(
        self,
        d_model=128,
        num_board_layers=6,
        use_bag=True,
        max_move_len=15,
    ):
        super().__init__()
        self.d_model = d_model
        self.use_bag = use_bag
        self.max_move_len = max_move_len

        # 0 empty, 1-26 A-Z, 27 blank
        self.letter_emb = nn.Embedding(28, d_model)

        # 0 normal, 1 DL, 2 TL, 3 DW, 4 TW
        self.premium_emb = nn.Embedding(5, d_model)

        # board positions 0..224 (15 x 15 = 225) L->R Top->Down
        self.board_pos_emb = nn.Embedding(225, d_model)

        self.board_blocks = nn.Sequential(
            *[ResidualCNNBlock(d_model) for _ in range(num_board_layers)]
        )

        rack_bag_dim = 54 if use_bag else 27

        self.rack_encoder = nn.Sequential(
            nn.Linear(rack_bag_dim, 256),
            nn.GELU(),
            nn.Linear(256, d_model),
            nn.GELU(),
        )

        self.move_letter_emb = nn.Embedding(28, d_model)
        self.move_pos_emb = nn.Embedding(max_move_len, d_model)

        self.move_numeric_encoder = nn.Sequential(
            nn.Linear(4, 64),   # row, col, direction, move_score
            nn.GELU(),
            nn.Linear(64, d_model),
            nn.GELU(),
        )

        self.move_encoder = nn.Sequential(
            nn.Linear(d_model * 2, d_model),
            nn.GELU(),
        )

        self.context_encoder = nn.Sequential(
            nn.Linear(2, 64),   # score_diff, tiles_remaining
            nn.GELU(),
            nn.Linear(64, d_model),
            nn.GELU(),
        )

        self.fusion = nn.Sequential(
            nn.Linear(d_model * 4, 512),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(512, 256),
            nn.GELU(),
            nn.Linear(256, d_model),
            nn.GELU(),
        )

        self.policy_head = nn.Linear(d_model, 1)
        self.equity_head = nn.Linear(d_model, 1)
        self.winprob_head = nn.Linear(d_model, 1)

    def encode_board(self, board_letters, board_premiums):
        """
        board_letters:  [B, 15, 15]
        board_premiums: [B, 15, 15]
        """

        B = board_letters.size(0)

        letter_x = self.letter_emb(board_letters)
        premium_x = self.premium_emb(board_premiums)

        pos_ids = torch.arange(225, device=board_letters.device)
        pos_ids = pos_ids.view(1, 15, 15).expand(B, 15, 15)
        pos_x = self.board_pos_emb(pos_ids)

        x = letter_x + premium_x + pos_x
        x = x.permute(0, 3, 1, 2)  # [B, 128, 15, 15]

        x = self.board_blocks(x)

        board_embed = x.mean(dim=(2, 3))  # [B, 128]
        return board_embed

    def encode_rack(self, rack_counts, bag_counts=None):
        """
        rack_counts: [B, 27]
        bag_counts:  [B, 27]
        """

        if self.use_bag:
            x = torch.cat([rack_counts, bag_counts], dim=-1)
        else:
            x = rack_counts

        return self.rack_encoder(x.float())

    def encode_move(
        self,
        move_letters,
        move_mask,
        move_position,
        move_direction,
        move_score,
    ):
        """
        move_letters:    [B, 15]
        move_mask:       [B, 15]
        move_position:   [B, 2]
        move_direction:  [B, 1]
        move_score:      [B, 1]
        """

        B, L = move_letters.shape

        letter_x = self.move_letter_emb(move_letters)

        pos_ids = torch.arange(L, device=move_letters.device)
        pos_ids = pos_ids.view(1, L).expand(B, L)
        pos_x = self.move_pos_emb(pos_ids)

        x = letter_x + pos_x  # [B, 15, 128]

        mask = move_mask.unsqueeze(-1).float()
        x = x * mask

        denom = mask.sum(dim=1).clamp(min=1.0)
        move_word_embed = x.sum(dim=1) / denom  # [B, 128]

        move_numeric = torch.cat(
            [
                move_position.float(),
                move_direction.float(),
                move_score.float(),
            ],
            dim=-1,
        )  # [B, 4]

        move_numeric_embed = self.move_numeric_encoder(move_numeric)

        move_embed = torch.cat(
            [move_word_embed, move_numeric_embed],
            dim=-1,
        )

        return self.move_encoder(move_embed)

    def forward(
        self,
        board_letters,
        board_premiums,
        rack_counts,
        bag_counts,
        move_letters,
        move_mask,
        move_position,
        move_direction,
        move_score,
        context,
    ):
        board_embed = self.encode_board(board_letters, board_premiums)
        rack_embed = self.encode_rack(rack_counts, bag_counts)
        move_embed = self.encode_move(
            move_letters,
            move_mask,
            move_position,
            move_direction,
            move_score,
        )
        context_embed = self.context_encoder(context.float())

        x = torch.cat(
            [board_embed, rack_embed, move_embed, context_embed],
            dim=-1,
        )

        x = self.fusion(x)

        policy_score = self.policy_head(x)
        equity = self.equity_head(x)
        win_prob = torch.sigmoid(self.winprob_head(x))

        return {
            "policy_score": policy_score,
            "equity": equity,
            "win_prob": win_prob,
        }