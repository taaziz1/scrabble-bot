from __future__ import annotations

import pickle
import random

from .bag import Bag
from .board import Board
from .config import GameConfig
from .cross_sets import CrossSets
from .dictionary import Dictionary
from gaddag.GADDAG import GADDAG
from .models import Tile
from .move import ExchangeMove, PassMove, PlayMove
from .rack import Rack
from .results import MoveResult, ValidationResult
from .rules import validate_move as rules_validate_move
from .scoring import score_play_move
from .state import GameState, PlayerState


class ScrabbleGame:
    def __init__(
        self,
        config: GameConfig,
        player_names: list[str],
        dictionary: Dictionary,
        gaddag: GADDAG | None = None,
        rng_seed: int | None = None,
    ) -> None:
        self._config = config
        self._dictionary = dictionary
        self._gaddag = gaddag
        self._rng = random.Random(rng_seed)
        self._cross_set = None
        self._state = self._new_game(player_names)

    def _new_game(self, player_names: list[str]) -> GameState:
        if not player_names:
            raise ValueError("At least one player is required.")

        if len(player_names) < 2:
            raise ValueError("Scrabble requires at least two players.")

        if len(set(player_names)) != len(player_names):
            raise ValueError("Player names must be unique.")

        board = Board(
            size=self._config.board_size,
            premium_squares=self._config.premium_squares,
        )

        if self._gaddag:
            self._cross_set = CrossSets(gaddag=self._gaddag)

        bag = Bag.from_distribution(
            tile_distribution=self._config.tile_distribution,
            tile_points=self._config.tile_points,
            rng=self._rng,
        )

        players: list[PlayerState] = []
        for name in player_names:
            players.append(
                PlayerState(
                    name=name,
                    rack=Rack(bag.draw(self._config.rack_size)),
                    score=0,
                )
            )

        return GameState(
            board=board,
            players=players,
            current_player_index=0,
            bag=bag,
            consecutive_scoreless_turns=0,
            is_finished=False,
            winner_index=None,
        )

    def get_state(self) -> GameState:
        return self._state

    def potential_moves(self, rack):
        return self._gaddag.generate_moves(self._state.board, self._cross_set, rack)

    def validate_move(self, move) -> ValidationResult:
        if self._state.is_finished:
            return ValidationResult(
                valid=False,
                errors=["Game is already finished."],
            )

        return rules_validate_move(
            state=self._state,
            move=move,
            config=self._config,
            dictionary=self._dictionary,
        )

    def apply_move(self, move) -> MoveResult:
        if self._state.is_finished:
            return MoveResult(
                state=self._state,
                words_formed=[],
                score_delta=0,
                game_over=True,
                errors=["Game is already finished."],
            )

        validation = self.validate_move(move)
        if not validation.valid:
            return MoveResult(
                state=self._state,
                words_formed=[],
                score_delta=0,
                game_over=self._state.is_finished,
                errors=validation.errors,
            )

        new_state = self._state
        current_player = new_state.players[new_state.current_player_index]

        words_formed = list(validation.words_formed)
        score_delta = 0

        if isinstance(move, PlayMove):
            score_delta = self._apply_play_move(
                state=new_state,
                move=move,
                validation=validation,
            )
            current_player.score += score_delta
            self._refill_rack(current_player.rack, new_state.bag)
            if self._cross_set:
                self._cross_set.update_cross_sets(new_state.board, move.placements, move.already_placed)
            new_state.consecutive_scoreless_turns = 0

        elif isinstance(move, ExchangeMove):
            self._apply_exchange_move(new_state, move)
            new_state.consecutive_scoreless_turns += 1

        elif isinstance(move, PassMove):
            new_state.consecutive_scoreless_turns += 1

        else:
            return MoveResult(
                state=self._state,
                words_formed=[],
                score_delta=0,
                game_over=self._state.is_finished,
                errors=["Unknown move type."],
            )

        self._finalize_game_if_needed(new_state)

        if not new_state.is_finished:
            new_state.current_player_index = self._next_player_index(new_state)

        return MoveResult(
            state=self._state,
            words_formed=words_formed,
            score_delta=score_delta,
            game_over=self._state.is_finished,
            errors=[],
        )

    def _apply_play_move(
        self,
        state: GameState,
        move: PlayMove,
        validation: ValidationResult,
    ) -> int:
        player = state.players[state.current_player_index]

        tiles_to_place: list[tuple[int, int, Tile]] = []
        for placement in move.placements:
            rack_tile = player.rack[placement.tile_index_in_rack]
            tile = self._resolve_tile_for_placement(
                rack_tile,
                placement.assigned_letter,
            )
            tiles_to_place.append((placement.row, placement.col, tile))

        state.board.place_tiles(tiles_to_place)

        used_indices = [placement.tile_index_in_rack for placement in move.placements]
        player.rack.remove_tiles_at(used_indices)

        if validation.word_cells and validation.newly_placed_positions:
            return score_play_move(
                word_cells=validation.word_cells,
                newly_placed_positions=validation.newly_placed_positions,
                config=self._config,
            )

        return validation.score

    def _apply_exchange_move(self, state: GameState, move: ExchangeMove) -> None:
        player = state.players[state.current_player_index]

        exchanged_tiles = player.rack.remove_tiles_at(list(move.tile_indices))
        new_tiles = state.bag.draw(len(exchanged_tiles))
        player.rack.add_tiles(new_tiles)
        state.bag.return_tiles(exchanged_tiles)

    def _refill_rack(self, rack: Rack, bag: Bag) -> None:
        missing = self._config.rack_size - len(rack)
        if missing > 0 and not bag.is_empty():
            rack.add_tiles(bag.draw(missing))

    def _next_player_index(self, state: GameState) -> int:
        return (state.current_player_index + 1) % len(state.players)

    def _finalize_game_if_needed(self, state: GameState) -> None:
        player_went_out = any(len(player.rack) == 0 for player in state.players) and state.bag.is_empty()
        too_many_scoreless_turns = state.consecutive_scoreless_turns >= len(state.players) * 2

        if not player_went_out and not too_many_scoreless_turns:
            return

        state.is_finished = True

        if player_went_out:
            self._apply_outplay_endgame_adjustments(state)

        state.winner_index = self._determine_winner_index(state)

    def _apply_outplay_endgame_adjustments(self, state: GameState) -> None:
        going_out_index = None
        for index, player in enumerate(state.players):
            if len(player.rack) == 0:
                going_out_index = index
                break

        if going_out_index is None:
            return

        total_unplayed_points = 0

        for index, player in enumerate(state.players):
            if index == going_out_index:
                continue

            rack_points = sum(0 if tile.is_blank else tile.points for tile in player.rack)
            player.score -= rack_points
            total_unplayed_points += rack_points

        state.players[going_out_index].score += total_unplayed_points

    def _determine_winner_index(self, state: GameState) -> int:
        best_index = 0
        best_score = state.players[0].score

        for index, player in enumerate(state.players[1:], start=1):
            if player.score > best_score:
                best_score = player.score
                best_index = index

        return best_index

    def _resolve_tile_for_placement(
        self,
        rack_tile: Tile,
        assigned_letter: str | None,
    ) -> Tile:
        if not rack_tile.is_blank:
            return rack_tile

        if not assigned_letter or len(assigned_letter) != 1 or not assigned_letter.isalpha():
            raise ValueError("Blank tiles must be assigned a single alphabetic letter.")

        return Tile(
            letter=assigned_letter.upper(),
            points=0,
            is_blank=True,
        )