from __future__ import annotations

from typing import Dict, List, Tuple, Set, Optional, Iterable
import time

from lib.Assignment import Assignment


class Solver:
    def __init__(self, s: str, t_patterns: List[str], R: Dict[str, Set[str]]):
        self.s: str = s
        self.t_patterns: List[str] = t_patterns
        self.R: Dict[str, Set[str]] = R

        self.variables: List[str] = sorted(R.keys())
        self.domains: Dict[str, Set[str]] = {g: set(vals) for g, vals in R.items()}

        self.tokenized_patterns: List[List[Tuple[str, str]]] = [self._tokenize(p) for p in t_patterns]
        self.occ: Dict[str, List[int]] = self._precompute_occurrences()

        # memoization cache for pattern feasibility under (pattern_idx, token_idx, i, assignment_key)
        self._fits_memo: Dict[Tuple[int, int, int, Tuple[Tuple[str, str], ...]], bool] = {}
        # initial candidate starts per pattern
        self.candidate_starts: List[Set[int]] = [self._initial_feasible_starts(idx) for idx in range(len(self.tokenized_patterns))]

        # search statistics
        self.states_explored: int = 0           # nodes entered (including root)
        self.states_considered: int = 0         # child assignments considered
        self.states_pruned: int = 0             # children cut by forward-check
        self.backtracks: int = 0                # times we returned None (dead end)
        self.solutions_found: int = 0
        self.max_depth_reached: int = 0
        self.solve_started_at: float = 0.0
        self.solve_ended_at: float = 0.0

        # print(f"variables: ({len(self.variables)}): {self.variables}")
        # print(f"domains: ({len(self.domains)}): {self.domains}")
        # print(f"tokenized_patterns: ({len(self.tokenized_patterns)}): {self.tokenized_patterns}")
        # print(f"occ: ({len(self.occ)}): {self.occ}")
        # print(f"candidate_starts: ({len(self.candidate_starts)}): {self.candidate_starts}")

    def solve(self) -> Optional[Assignment]:
        assignment: Dict[str, str] = {}

        # reset stats for a fresh run (start timer immediately, even if quick-fail)
        self.solve_started_at = time.perf_counter()
        self.states_explored = 0
        self.states_considered = 0
        self.states_pruned = 0
        self.backtracks = 0
        self.solutions_found = 0
        self.max_depth_reached = 0
        self._fits_memo.clear()

        # quick fail if any pattern has no feasible start initially
        initial_infeasible = sum(1 for c in self.candidate_starts if len(c) == 0)
        if initial_infeasible > 0:
            # count root explored and a backtrack due to infeasibility at depth 0
            self.states_explored = 1
            self.backtracks = 1
            self._initial_infeasible = initial_infeasible
            self.solve_ended_at = time.perf_counter()
            return None
        else:
            self._initial_infeasible = 0

        result = self._dfs(assignment, self.candidate_starts)
        self.solve_ended_at = time.perf_counter()
        if result is None:
            return None
        return Assignment(result)

    def _dfs(self, assignment: Dict[str, str], candidate_starts: List[Set[int]]) -> Optional[Dict[str, str]]:
        # enter node
        self.states_explored += 1
        depth = len(assignment)
        if depth > self.max_depth_reached:
            self.max_depth_reached = depth
        
        # all assigned -> success (candidate_starts non-empty by invariant)
        if len(assignment) == len(self.variables):
            self.solutions_found += 1
            return assignment

        # MRV: unassigned variable with smallest domain size
        unassigned: List[str] = [v for v in self.variables if v not in assignment]
        mrv_var: str = min(unassigned, key=lambda v: len(self.domains[v]))

        # Tight-context tiebreaker: reduce placements based on local contexts
        # Value ordering: fewest placements first
        ordered_values = sorted(self.domains[mrv_var], key=lambda r: self._value_placement_score(mrv_var, r, assignment, candidate_starts))

        for value in ordered_values:
            self.states_considered += 1
            # assign and forward check
            new_assignment = dict(assignment)
            new_assignment[mrv_var] = value

            new_cand = self._update_all_candidate_starts(new_assignment, candidate_starts)
            if new_cand is None:
                self.states_pruned += 1
                continue

            res = self._dfs(new_assignment, new_cand)
            if res is not None:
                return res

        # dead end
        self.backtracks += 1
        return None

    def _tokenize(self, pattern: str) -> List[Tuple[str, str]]:
        tokens: List[Tuple[str, str]] = []
        for ch in pattern:
            if 'A' <= ch <= 'Z':
                tokens.append(('var', ch))
            else:
                tokens.append(('lit', ch))
        return tokens

    def _precompute_occurrences(self) -> Dict[str, List[int]]:
        occ: Dict[str, List[int]] = {}
        for vals in self.R.values():
            for r in vals:
                if r in occ:
                    continue
                occ[r] = self._find_occurrences(self.s, r)
        return occ

    def _find_occurrences(self, s: str, sub: str) -> List[int]:
        positions: List[int] = []
        start = 0
        # allow overlapping occurrences
        while True:
            idx = s.find(sub, start)
            if idx == -1:
                break
            positions.append(idx)
            start = idx + 1
        return positions

    def _value_placement_score(self, var: str, value: str, assignment: Dict[str, str]) -> int:
        # Heuristic: aggregate count of feasible starts across patterns when var=value
        # Lower is better (tighter context)
        trial_assignment = dict(assignment)
        trial_assignment[var] = value
        score = 0
        for tokens, cand in zip(self.tokenized_patterns, self.candidate_starts):
            if len(cand) == 0:
                return 10**9
            count = 0
            for start_pos in cand:
                if self._pattern_fits_at(tokens, start_pos, trial_assignment):
                    count += 1
            score += count
        return score

    def _domain_sizes(self) -> List[int]:
        return [len(self.domains[v]) for v in self.variables]

    def compute_totals(self) -> Tuple[int, int]:
        # returns (total_leaf_assignments, total_nodes_in_full_tree)
        sizes = self._domain_sizes()
        total_assignments = 1
        for d in sizes:
            total_assignments *= d
        # total nodes = 1 (root) + sum of prefix products
        prefix = 1
        total_nodes = 1
        for d in sizes:
            prefix *= d
            total_nodes += prefix
        return total_assignments, total_nodes

    def print_stats(self) -> None:
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        CYAN = "\033[96m"
        RED = "\033[91m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        leaves, total_nodes = self.compute_totals()

        print()
        print(f"{BOLD}{CYAN}Search statistics:{RESET}")
        if getattr(self, "_initial_infeasible", 0) > 0:
            print(f"{RED}• Initial feasibility failed for {self._initial_infeasible} pattern(s){RESET}")
        print(f"🌳 Total tree nodes (theoretical): {YELLOW}{total_nodes}{RESET}")
        print(f"🍃 Total leaf assignments (theoretical): {YELLOW}{leaves}{RESET}")
        print(f"🔎 States explored: {GREEN}{self.states_explored}{RESET}")
        print(f"🧭 States considered: {GREEN}{self.states_considered}{RESET}")
        print(f"✂️  States pruned: {RED}{self.states_pruned}{RESET}")
        print(f"↩️  Backtracks: {RED}{self.backtracks}{RESET}")
        print(f"📏 Max depth reached: {GREEN}{self.max_depth_reached}{RESET}")
        print(f"✅ Solutions found: {GREEN}{self.solutions_found}{RESET}")
        elapsed_s = max(0.0, self.solve_ended_at - self.solve_started_at)
        print(f"⏱  Time: {YELLOW}{elapsed_s*1000:.2f} ms{RESET}")

    def _initial_feasible_starts(self, pattern_idx: int) -> Set[int]:
        starts: Set[int] = set()
        for pos in range(0, len(self.s)):
            if self._pattern_fits_at(pattern_idx, 0, pos, {}):
                starts.add(pos)
        return starts

    def _update_all_candidate_starts(self, assignment: Dict[str, str], candidate_starts: List[Set[int]]) -> Optional[List[Set[int]]]:
        updated: List[Set[int]] = []
        for pat_idx, cand in enumerate(candidate_starts):
            new_cand: Set[int] = set()
            for pos in cand:
                if self._pattern_fits_at(pat_idx, 0, pos, assignment):
                    new_cand.add(pos)
            if len(new_cand) == 0:
                return None
            updated.append(new_cand)
        return updated

    def _pattern_fits_at(self, pattern_idx: int, token_idx: int, i: int, assignment: Dict[str, str]) -> bool:
        tokens = self.tokenized_patterns[pattern_idx]
        assignment_key: Tuple[Tuple[str, str], ...] = tuple(sorted(assignment.items()))
        memo_key = (pattern_idx, token_idx, i, assignment_key)
        if memo_key in self._fits_memo:
            return self._fits_memo[memo_key]

        if token_idx == len(tokens):
            result = True
        elif i > len(self.s):
            result = False
        else:
            kind, val = tokens[token_idx]
            if kind == 'lit':
                if i >= len(self.s) or self.s[i] != val:
                    result = False
                else:
                    result = self._pattern_fits_at(pattern_idx, token_idx + 1, i + 1, assignment)
            else:
                var = val
                if var in assignment:
                    r = assignment[var]
                    end = i + len(r)
                    if end > len(self.s) or self.s[i:end] != r:
                        result = False
                    else:
                        result = self._pattern_fits_at(pattern_idx, token_idx + 1, end, assignment)
                else:
                    # try any domain value that matches here
                    result = False
                    for r in self.domains[var]:
                        end = i + len(r)
                        if end <= len(self.s) and self.s[i:end] == r:
                            if self._pattern_fits_at(pattern_idx, token_idx + 1, end, assignment):
                                result = True
                                break

        self._fits_memo[memo_key] = result
        return result

    def _value_placement_score(self, var: str, value: str, assignment: Dict[str, str], candidate_starts: List[Set[int]]) -> int:
        # Heuristic: aggregate count of feasible starts across patterns when var=value
        trial_assignment = dict(assignment)
        trial_assignment[var] = value
        score = 0
        for pat_idx, cand in enumerate(candidate_starts):
            if len(cand) == 0:
                return 10**9
            count = 0
            for start_pos in cand:
                if self._pattern_fits_at(pat_idx, 0, start_pos, trial_assignment):
                    count += 1
            score += count
        return score


