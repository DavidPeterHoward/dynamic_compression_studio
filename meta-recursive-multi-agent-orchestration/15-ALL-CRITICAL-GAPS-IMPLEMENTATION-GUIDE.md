# All Critical Gaps - Complete Implementation Guide
## 21 Must-Have Components for Production-Ready AI System

---

## EXECUTIVE SUMMARY

This document provides **complete implementation specifications** for all 21 CRITICAL gaps identified in the multi-dimensional gap analysis. These gaps must be addressed before production deployment.

**Priority Level:** CRITICAL  
**Total Implementation Effort:** 48 person-weeks  
**Recommended Timeline:** 8 weeks with 6-person team  
**Risk if Not Addressed:** HIGH - System unsafe for production use

---

## TABLE OF CONTENTS

### Logic & Reasoning (4 Critical Gaps)
1. [Non-Monotonic Reasoning](#1-non-monotonic-reasoning)
2. [Fuzzy Logic System](#2-fuzzy-logic-system)

### Communication & Semantics (2 Critical Gaps)
3. [Speech Act Framework](#3-speech-act-framework)
4. [Formal Ontology (OWL/RDF)](#4-formal-ontology-owlrdf)

### Implementation & Resilience (3 Critical Gaps)
5. [Circuit Breaker Pattern](#5-circuit-breaker-pattern)
6. [Saga Transaction Pattern](#6-saga-transaction-pattern)
7. [Rate Limiting & Backpressure](#7-rate-limiting--backpressure)

### Safety & Ethics (4 Critical Gaps)
8. [Value Alignment Monitor](#8-value-alignment-monitor)
9. [Corrigibility Enforcer](#9-corrigibility-enforcer)
10. [Safety Tripwire System](#10-safety-tripwire-system)
11. [Bias Detection Framework](#11-bias-detection-framework)

### Human-AI Interaction (4 Critical Gaps)
12. [Trust Calibration](#12-trust-calibration)
13. [Cognitive Load Management](#13-cognitive-load-management)
14. [Mental Model Building](#14-mental-model-building)
15. [Expectation Management](#15-expectation-management)

### Meta-Cognition (4 Critical Gaps)
16. [Self-Awareness Mechanism](#16-self-awareness-mechanism)
17. [Confidence Calibration](#17-confidence-calibration)
18. [Known Unknown Tracking](#18-known-unknown-tracking)
19. [Learning Strategy Selection](#19-learning-strategy-selection)

### Additional Critical Components (2 Critical Gaps)
20. [Abductive Reasoning Engine](#20-abductive-reasoning-engine)
21. [Explainability Framework (LIME/SHAP)](#21-explainability-framework-limeshap)

---

## CRITICAL GAP IMPLEMENTATIONS

---

## 1. NON-MONOTONIC REASONING

### 1.1 Overview

**What:** Logic system that allows beliefs to be retracted when new information contradicts old assumptions.

**Why Critical:** AI agents must handle belief updates, default assumptions, and exceptions without logical explosion.

**Use Cases:**
- "Birds can fly" (default) → "Penguins can't fly" (exception)
- Agent believes task will succeed → new information suggests failure → revise belief
- Provisional reasoning with incomplete information

### 1.2 Complete Implementation

```python
# ============================================================================
# NON-MONOTONIC REASONING ENGINE
# ============================================================================

from enum import Enum
from typing import Set, List, Dict, Optional, Tuple
from dataclasses import dataclass
import networkx as nx

class JustificationType(Enum):
    """Types of justification for beliefs"""
    STRICT = "strict"           # Must be true (monotonic)
    DEFAULT = "default"         # True by default, can be overridden
    DEFEASIBLE = "defeasible"   # Can be defeated by exceptions
    ASSUMPTION = "assumption"   # Tentative, pending confirmation

@dataclass
class Belief:
    """Represents a belief in the knowledge base"""
    proposition: str
    justification_type: JustificationType
    support: Set[str]           # Set of supporting beliefs
    confidence: float = 1.0
    defeated_by: Set[str] = None
    
    def __post_init__(self):
        if self.defeated_by is None:
            self.defeated_by = set()

@dataclass
class DefaultRule:
    """Represents a default reasoning rule"""
    prerequisites: Set[str]     # What must be true
    conclusion: str             # What to conclude
    exceptions: Set[str]        # What defeats this rule
    priority: int = 0           # Higher priority rules win conflicts

class NonMonotonicReasoner:
    """
    Implements default logic and non-monotonic reasoning.
    
    Based on Reiter's Default Logic:
    - Normal defaults: (P : Q) / R
    - "If P is true and Q is consistent, conclude R"
    """
    
    def __init__(self):
        self.beliefs: Dict[str, Belief] = {}
        self.default_rules: List[DefaultRule] = []
        self.strict_rules: List[Tuple[Set[str], str]] = []
        self.dependency_graph = nx.DiGraph()
        
    # -----------------------------------------------------------------------
    # BELIEF MANAGEMENT
    # -----------------------------------------------------------------------
    
    def add_strict_belief(self, proposition: str, support: Set[str] = None):
        """Add a belief that cannot be retracted (monotonic)"""
        if support is None:
            support = set()
            
        belief = Belief(
            proposition=proposition,
            justification_type=JustificationType.STRICT,
            support=support,
            confidence=1.0
        )
        
        self.beliefs[proposition] = belief
        self._update_dependency_graph(proposition, support)
        
    def add_default_belief(self, proposition: str, support: Set[str] = None,
                          defeated_by: Set[str] = None, confidence: float = 0.8):
        """Add a default belief that can be overridden"""
        if support is None:
            support = set()
        if defeated_by is None:
            defeated_by = set()
            
        belief = Belief(
            proposition=proposition,
            justification_type=JustificationType.DEFAULT,
            support=support,
            confidence=confidence,
            defeated_by=defeated_by
        )
        
        self.beliefs[proposition] = belief
        self._update_dependency_graph(proposition, support)
        
    def add_default_rule(self, prerequisites: Set[str], conclusion: str,
                        exceptions: Set[str] = None, priority: int = 0):
        """Add a default reasoning rule"""
        if exceptions is None:
            exceptions = set()
            
        rule = DefaultRule(
            prerequisites=prerequisites,
            conclusion=conclusion,
            exceptions=exceptions,
            priority=priority
        )
        
        self.default_rules.append(rule)
        
    # -----------------------------------------------------------------------
    # REASONING
    # -----------------------------------------------------------------------
    
    def is_believed(self, proposition: str, 
                   check_defeated: bool = True) -> bool:
        """Check if proposition is currently believed"""
        if proposition not in self.beliefs:
            return False
            
        belief = self.beliefs[proposition]
        
        if not check_defeated:
            return True
            
        # Check if belief is defeated
        if belief.justification_type == JustificationType.STRICT:
            return True  # Strict beliefs cannot be defeated
            
        # Check if any defeater is present
        for defeater in belief.defeated_by:
            if self.is_believed(defeater, check_defeated=False):
                return False  # Belief is defeated
                
        return True
        
    def apply_default_rules(self) -> Set[str]:
        """Apply all applicable default rules and return new conclusions"""
        new_conclusions = set()
        
        # Sort rules by priority (higher first)
        sorted_rules = sorted(self.default_rules, 
                            key=lambda r: r.priority, 
                            reverse=True)
        
        for rule in sorted_rules:
            if self._rule_applicable(rule):
                # Check if conclusion already believed
                if not self.is_believed(rule.conclusion, check_defeated=False):
                    # Add as default belief
                    self.add_default_belief(
                        proposition=rule.conclusion,
                        support=rule.prerequisites,
                        defeated_by=rule.exceptions,
                        confidence=0.9
                    )
                    new_conclusions.add(rule.conclusion)
                    
        return new_conclusions
        
    def _rule_applicable(self, rule: DefaultRule) -> bool:
        """Check if a default rule is applicable"""
        # All prerequisites must be believed
        for prereq in rule.prerequisites:
            if not self.is_believed(prereq):
                return False
                
        # No exception should be believed
        for exception in rule.exceptions:
            if self.is_believed(exception):
                return False
                
        return True
        
    # -----------------------------------------------------------------------
    # BELIEF REVISION
    # -----------------------------------------------------------------------
    
    def revise_beliefs(self, new_information: Set[str]):
        """
        Revise belief set given new information.
        Uses AGM (Alchourrón, Gärdenfors, Makinson) belief revision.
        """
        # Add new information as strict beliefs
        for info in new_information:
            self.add_strict_belief(info)
            
        # Identify conflicts
        conflicts = self._identify_conflicts()
        
        # Resolve conflicts by retracting lower-priority beliefs
        self._resolve_conflicts(conflicts)
        
        # Propagate changes through dependency graph
        self._propagate_revisions()
        
        # Re-apply default rules
        self.apply_default_rules()
        
    def _identify_conflicts(self) -> List[Tuple[str, str]]:
        """Identify pairs of conflicting beliefs"""
        conflicts = []
        
        for prop1, belief1 in self.beliefs.items():
            for prop2, belief2 in self.beliefs.items():
                if prop1 != prop2:
                    if self._contradicts(prop1, prop2):
                        conflicts.append((prop1, prop2))
                        
        return conflicts
        
    def _contradicts(self, prop1: str, prop2: str) -> bool:
        """Check if two propositions contradict"""
        # Simple negation check
        if prop1.startswith("NOT_") and prop1[4:] == prop2:
            return True
        if prop2.startswith("NOT_") and prop2[4:] == prop1:
            return True
            
        # Could extend with more sophisticated contradiction detection
        return False
        
    def _resolve_conflicts(self, conflicts: List[Tuple[str, str]]):
        """Resolve conflicts by retracting lower-priority beliefs"""
        for prop1, prop2 in conflicts:
            belief1 = self.beliefs[prop1]
            belief2 = self.beliefs[prop2]
            
            # Strict beliefs always win
            if belief1.justification_type == JustificationType.STRICT:
                if belief2.justification_type != JustificationType.STRICT:
                    self._retract_belief(prop2)
            elif belief2.justification_type == JustificationType.STRICT:
                self._retract_belief(prop1)
            else:
                # Both are non-strict, compare confidence
                if belief1.confidence > belief2.confidence:
                    self._retract_belief(prop2)
                else:
                    self._retract_belief(prop1)
                    
    def _retract_belief(self, proposition: str):
        """Retract a belief and all beliefs that depend on it"""
        if proposition not in self.beliefs:
            return
            
        # Find all dependent beliefs
        dependents = self._find_dependents(proposition)
        
        # Retract them in reverse dependency order
        for dependent in reversed(list(nx.topological_sort(
            self.dependency_graph.subgraph(dependents)
        ))):
            if dependent in self.beliefs:
                del self.beliefs[dependent]
                
    def _find_dependents(self, proposition: str) -> Set[str]:
        """Find all beliefs that depend on this proposition"""
        if proposition not in self.dependency_graph:
            return set()
            
        return set(nx.descendants(self.dependency_graph, proposition))
        
    def _update_dependency_graph(self, proposition: str, support: Set[str]):
        """Update dependency graph with new belief"""
        self.dependency_graph.add_node(proposition)
        
        for supporter in support:
            self.dependency_graph.add_edge(supporter, proposition)
            
    def _propagate_revisions(self):
        """Propagate revisions through belief network"""
        # Re-evaluate all non-strict beliefs
        to_reevaluate = [
            (prop, belief) for prop, belief in self.beliefs.items()
            if belief.justification_type != JustificationType.STRICT
        ]
        
        for prop, belief in to_reevaluate:
            # Check if all support is still present
            if not all(self.is_believed(s) for s in belief.support):
                self._retract_belief(prop)
                
    # -----------------------------------------------------------------------
    # QUERY INTERFACE
    # -----------------------------------------------------------------------
    
    def query(self, proposition: str) -> Dict:
        """Query whether proposition is believed and why"""
        believed = self.is_believed(proposition)
        
        result = {
            'proposition': proposition,
            'believed': believed,
            'exists': proposition in self.beliefs
        }
        
        if proposition in self.beliefs:
            belief = self.beliefs[proposition]
            result.update({
                'justification_type': belief.justification_type.value,
                'confidence': belief.confidence,
                'support': list(belief.support),
                'defeated_by': list(belief.defeated_by),
                'is_defeated': not believed and result['exists']
            })
            
        return result
        
    def explain_reasoning(self, proposition: str) -> str:
        """Generate natural language explanation of reasoning"""
        if proposition not in self.beliefs:
            return f"I don't have any information about '{proposition}'."
            
        belief = self.beliefs[proposition]
        believed = self.is_believed(proposition)
        
        if belief.justification_type == JustificationType.STRICT:
            explanation = f"I believe '{proposition}' with certainty because "
            if belief.support:
                explanation += f"it follows from {', '.join(belief.support)}."
            else:
                explanation += "it was given as a fact."
        else:
            if believed:
                explanation = f"I believe '{proposition}' by default "
                explanation += f"(confidence: {belief.confidence:.0%}) because "
                if belief.support:
                    explanation += f"{', '.join(belief.support)} hold(s). "
                else:
                    explanation += "it's a default assumption. "
                    
                if belief.defeated_by:
                    explanation += f"This could be defeated by {', '.join(belief.defeated_by)}, "
                    explanation += "but none of those are currently believed."
            else:
                explanation = f"I no longer believe '{proposition}' because "
                active_defeaters = [
                    d for d in belief.defeated_by 
                    if self.is_believed(d, check_defeated=False)
                ]
                explanation += f"it's defeated by {', '.join(active_defeaters)}."
                
        return explanation
        
    # -----------------------------------------------------------------------
    # UTILITY
    # -----------------------------------------------------------------------
    
    def get_all_beliefs(self, include_defeated: bool = False) -> Dict[str, Belief]:
        """Get all current beliefs"""
        if include_defeated:
            return self.beliefs.copy()
        else:
            return {
                prop: belief for prop, belief in self.beliefs.items()
                if self.is_believed(prop)
            }
            
    def get_belief_hierarchy(self) -> Dict:
        """Get beliefs organized by justification type"""
        hierarchy = {
            'strict': [],
            'default': [],
            'defeasible': [],
            'defeated': []
        }
        
        for prop, belief in self.beliefs.items():
            if not self.is_believed(prop):
                hierarchy['defeated'].append(prop)
            else:
                hierarchy[belief.justification_type.value].append(prop)
                
        return hierarchy


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_bird_reasoning():
    """Classic example: birds fly, except penguins"""
    reasoner = NonMonotonicReasoner()
    
    # Add default rule: Birds typically fly
    reasoner.add_default_rule(
        prerequisites={'IS_BIRD'},
        conclusion='CAN_FLY',
        exceptions={'IS_PENGUIN', 'IS_OSTRICH'},
        priority=1
    )
    
    # Tweety is a bird
    reasoner.add_strict_belief('IS_BIRD_TWEETY')
    reasoner.add_strict_belief('IS_BIRD', support={'IS_BIRD_TWEETY'})
    
    # Apply default reasoning
    reasoner.apply_default_rules()
    
    print("Initial belief:")
    print(reasoner.explain_reasoning('CAN_FLY'))
    # Output: "I believe 'CAN_FLY' by default (confidence: 90%) because IS_BIRD holds..."
    
    # New information: Tweety is a penguin!
    print("\nNew information: Tweety is a penguin")
    reasoner.revise_beliefs({'IS_PENGUIN'})
    
    print("Revised belief:")
    print(reasoner.explain_reasoning('CAN_FLY'))
    # Output: "I no longer believe 'CAN_FLY' because it's defeated by IS_PENGUIN."


def example_agent_task_reasoning():
    """Example: Agent reasoning about task success"""
    reasoner = NonMonotonicReasoner()
    
    # Default: If agent is capable and not overloaded, task will succeed
    reasoner.add_default_rule(
        prerequisites={'AGENT_CAPABLE', 'AGENT_NOT_OVERLOADED'},
        conclusion='TASK_WILL_SUCCEED',
        exceptions={'TASK_TOO_COMPLEX', 'NETWORK_FAILURE'},
        priority=2
    )
    
    # Initial state
    reasoner.add_strict_belief('AGENT_CAPABLE')
    reasoner.add_default_belief('AGENT_NOT_OVERLOADED', confidence=0.7)
    
    reasoner.apply_default_rules()
    
    print(reasoner.query('TASK_WILL_SUCCEED'))
    # {'proposition': 'TASK_WILL_SUCCEED', 'believed': True, ...}
    
    # New information: Task is too complex
    reasoner.revise_beliefs({'TASK_TOO_COMPLEX'})
    
    print(reasoner.query('TASK_WILL_SUCCEED'))
    # {'proposition': 'TASK_WILL_SUCCEED', 'believed': False, 'is_defeated': True, ...}


# ============================================================================
# TESTING
# ============================================================================

def test_non_monotonic_reasoning():
    """Comprehensive tests for non-monotonic reasoner"""
    
    def test_default_reasoning():
        reasoner = NonMonotonicReasoner()
        reasoner.add_default_rule({'A'}, 'B')
        reasoner.add_strict_belief('A')
        reasoner.apply_default_rules()
        assert reasoner.is_believed('B'), "Default rule should fire"
        
    def test_exception_handling():
        reasoner = NonMonotonicReasoner()
        reasoner.add_default_rule({'A'}, 'B', exceptions={'C'})
        reasoner.add_strict_belief('A')
        reasoner.add_strict_belief('C')
        reasoner.apply_default_rules()
        assert not reasoner.is_believed('B'), "Exception should block default"
        
    def test_belief_revision():
        reasoner = NonMonotonicReasoner()
        reasoner.add_default_belief('A')
        assert reasoner.is_believed('A')
        
        reasoner.revise_beliefs({'NOT_A'})
        assert not reasoner.is_believed('A'), "Belief should be revised"
        
    def test_priority_resolution():
        reasoner = NonMonotonicReasoner()
        reasoner.add_default_rule({'A'}, 'B', priority=1)
        reasoner.add_default_rule({'A'}, 'NOT_B', priority=2)
        reasoner.add_strict_belief('A')
        reasoner.apply_default_rules()
        
        assert reasoner.is_believed('NOT_B'), "Higher priority rule should win"
        assert not reasoner.is_believed('B')
        
    # Run all tests
    test_default_reasoning()
    test_exception_handling()
    test_belief_revision()
    test_priority_resolution()
    
    print("✓ All non-monotonic reasoning tests passed")


# ============================================================================
# INTEGRATION WITH AGENT SYSTEM
# ============================================================================

class ReasoningAgent:
    """Agent with non-monotonic reasoning capability"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.reasoner = NonMonotonicReasoner()
        self._initialize_default_rules()
        
    def _initialize_default_rules(self):
        """Set up domain-specific default rules"""
        
        # Task success reasoning
        self.reasoner.add_default_rule(
            prerequisites={'HAS_CAPABILITY', 'LOW_LOAD'},
            conclusion='CAN_COMPLETE_TASK',
            exceptions={'TASK_TOO_HARD', 'TIME_CONSTRAINT_VIOLATED'},
            priority=3
        )
        
        # Resource availability
        self.reasoner.add_default_rule(
            prerequisites={'RESOURCE_AVAILABLE'},
            conclusion='CAN_USE_RESOURCE',
            exceptions={'RESOURCE_LOCKED', 'INSUFFICIENT_PERMISSIONS'},
            priority=2
        )
        
    def update_belief(self, belief: str, is_strict: bool = False):
        """Update agent's beliefs"""
        if is_strict:
            self.reasoner.add_strict_belief(belief)
        else:
            self.reasoner.add_default_belief(belief)
            
        # Apply reasoning
        self.reasoner.apply_default_rules()
        
    def receive_information(self, information: Set[str]):
        """Receive new information and revise beliefs"""
        self.reasoner.revise_beliefs(information)
        
    def believes(self, proposition: str) -> bool:
        """Check if agent believes proposition"""
        return self.reasoner.is_believed(proposition)
        
    def explain_belief(self, proposition: str) -> str:
        """Explain why agent believes or doesn't believe proposition"""
        return self.reasoner.explain_reasoning(proposition)
```

### 1.3 Integration Points

**Where to Use:**
- Agent belief management
- Task feasibility assessment
- Contradiction resolution
- Assumption handling
- Dynamic world modeling

**Dependencies:**
- None (standalone component)

**Performance:**
- Belief check: O(d) where d = dependency depth
- Rule application: O(r × p) where r = rules, p = propositions
- Belief revision: O(n × log n) where n = beliefs

### 1.4 Testing Strategy

```python
Test Cases:
1. Default rule application
2. Exception handling
3. Belief revision with contradictions
4. Priority-based conflict resolution
5. Dependency propagation
6. Circular dependency detection
7. Explanation generation
8. Integration with agent decision-making
```

### 1.5 Metrics

- **Coverage:** Number of default rules defined
- **Revision Frequency:** How often beliefs are revised
- **Conflict Rate:** Percentage of beliefs that conflict
- **Explanation Quality:** Human evaluation of explanations

---

## 2. FUZZY LOGIC SYSTEM

### 2.1 Overview

**What:** Logic system with continuous truth values [0,1] instead of binary {0,1}.

**Why Critical:** Real-world properties (agent capability, task complexity) are not binary but matters of degree.

**Use Cases:**
- "How capable is this agent?" → 0.73 (quite capable)
- "How complex is this task?" → 0.85 (very complex)
- "How confident am I?" → 0.62 (moderately confident)

### 2.2 Complete Implementation

```python
# ============================================================================
# FUZZY LOGIC ENGINE
# ============================================================================

import numpy as np
from typing import Callable, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class MembershipFunction(Enum):
    """Types of fuzzy membership functions"""
    TRIANGULAR = "triangular"
    TRAPEZOIDAL = "trapezoidal"
    GAUSSIAN = "gaussian"
    SIGMOID = "sigmoid"

@dataclass
class FuzzySet:
    """Represents a fuzzy set with membership function"""
    name: str
    membership_func: Callable[[float], float]
    universe_min: float
    universe_max: float
    
    def membership(self, x: float) -> float:
        """Get membership degree of x in this fuzzy set"""
        if x < self.universe_min or x > self.universe_max:
            return 0.0
        return self.membership_func(x)

class FuzzyVariable:
    """Represents a fuzzy linguistic variable"""
    
    def __init__(self, name: str, universe_min: float, universe_max: float):
        self.name = name
        self.universe_min = universe_min
        self.universe_max = universe_max
        self.fuzzy_sets: Dict[str, FuzzySet] = {}
        
    def add_fuzzy_set(self, set_name: str, membership_func: Callable[[float], float]):
        """Add a fuzzy set to this variable"""
        fuzzy_set = FuzzySet(
            name=set_name,
            membership_func=membership_func,
            universe_min=self.universe_min,
            universe_max=self.universe_max
        )
        self.fuzzy_sets[set_name] = fuzzy_set
        
    def fuzzify(self, crisp_value: float) -> Dict[str, float]:
        """Convert crisp value to fuzzy membership degrees"""
        return {
            name: fset.membership(crisp_value)
            for name, fset in self.fuzzy_sets.items()
        }

# Membership function constructors
def triangular(a: float, b: float, c: float) -> Callable[[float], float]:
    """Create triangular membership function"""
    def membership(x: float) -> float:
        if x <= a or x >= c:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a)
        else:  # b < x < c
            return (c - x) / (c - b)
    return membership

def trapezoidal(a: float, b: float, c: float, d: float) -> Callable[[float], float]:
    """Create trapezoidal membership function"""
    def membership(x: float) -> float:
        if x <= a or x >= d:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a)
        elif b < x <= c:
            return 1.0
        else:  # c < x < d
            return (d - x) / (d - c)
    return membership

def gaussian(mean: float, std: float) -> Callable[[float], float]:
    """Create Gaussian membership function"""
    def membership(x: float) -> float:
        return np.exp(-((x - mean) ** 2) / (2 * std ** 2))
    return membership

@dataclass
class FuzzyRule:
    """Represents a fuzzy if-then rule"""
    antecedents: List[Tuple[str, str]]  # [(variable, fuzzy_set), ...]
    consequent: Tuple[str, str]         # (variable, fuzzy_set)
    weight: float = 1.0

class FuzzyInferenceSystem:
    """
    Mamdani-style fuzzy inference system.
    
    Steps:
    1. Fuzzification: Convert crisp inputs to fuzzy degrees
    2. Rule evaluation: Apply fuzzy rules
    3. Aggregation: Combine rule outputs
    4. Defuzzification: Convert fuzzy output to crisp value
    """
    
    def __init__(self):
        self.input_variables: Dict[str, FuzzyVariable] = {}
        self.output_variables: Dict[str, FuzzyVariable] = {}
        self.rules: List[FuzzyRule] = []
        
    # -----------------------------------------------------------------------
    # VARIABLE MANAGEMENT
    # -----------------------------------------------------------------------
    
    def add_input_variable(self, name: str, universe_min: float, universe_max: float):
        """Add an input variable"""
        self.input_variables[name] = FuzzyVariable(name, universe_min, universe_max)
        
    def add_output_variable(self, name: str, universe_min: float, universe_max: float):
        """Add an output variable"""
        self.output_variables[name] = FuzzyVariable(name, universe_min, universe_max)
        
    def add_fuzzy_set_to_input(self, var_name: str, set_name: str, 
                                membership_func: Callable[[float], float]):
        """Add fuzzy set to input variable"""
        self.input_variables[var_name].add_fuzzy_set(set_name, membership_func)
        
    def add_fuzzy_set_to_output(self, var_name: str, set_name: str,
                                 membership_func: Callable[[float], float]):
        """Add fuzzy set to output variable"""
        self.output_variables[var_name].add_fuzzy_set(set_name, membership_func)
        
    # -----------------------------------------------------------------------
    # RULE MANAGEMENT
    # -----------------------------------------------------------------------
    
    def add_rule(self, antecedents: List[Tuple[str, str]], 
                consequent: Tuple[str, str], weight: float = 1.0):
        """
        Add a fuzzy rule.
        
        Example:
            IF complexity is HIGH AND capability is LOW THEN success is LOW
            
            add_rule(
                antecedents=[('complexity', 'HIGH'), ('capability', 'LOW')],
                consequent=('success', 'LOW'),
                weight=1.0
            )
        """
        rule = FuzzyRule(antecedents, consequent, weight)
        self.rules.append(rule)
        
    # -----------------------------------------------------------------------
    # INFERENCE
    # -----------------------------------------------------------------------
    
    def infer(self, inputs: Dict[str, float]) -> Dict[str, float]:
        """
        Perform fuzzy inference.
        
        Args:
            inputs: Dict mapping input variable names to crisp values
            
        Returns:
            Dict mapping output variable names to crisp values
        """
        # Step 1: Fuzzification
        fuzzified = self._fuzzify(inputs)
        
        # Step 2 & 3: Rule evaluation and aggregation
        aggregated = self._evaluate_and_aggregate(fuzzified)
        
        # Step 4: Defuzzification
        outputs = self._defuzzify(aggregated)
        
        return outputs
        
    def _fuzzify(self, inputs: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Convert crisp inputs to fuzzy membership degrees"""
        fuzzified = {}
        
        for var_name, crisp_value in inputs.items():
            if var_name not in self.input_variables:
                raise ValueError(f"Unknown input variable: {var_name}")
                
            fuzzified[var_name] = self.input_variables[var_name].fuzzify(crisp_value)
            
        return fuzzified
        
    def _evaluate_and_aggregate(self, fuzzified: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, List[float]]]:
        """Evaluate rules and aggregate results"""
        # Initialize output accumulator
        output_accumulator = {
            var_name: {set_name: [] for set_name in var.fuzzy_sets}
            for var_name, var in self.output_variables.items()
        }
        
        # Evaluate each rule
        for rule in self.rules:
            # Compute rule firing strength (minimum of antecedent memberships)
            firing_strength = min(
                fuzzified[var_name][set_name]
                for var_name, set_name in rule.antecedents
            )
            
            # Apply rule weight
            firing_strength *= rule.weight
            
            # Add to output accumulator
            out_var, out_set = rule.consequent
            output_accumulator[out_var][out_set].append(firing_strength)
            
        return output_accumulator
        
    def _defuzzify(self, aggregated: Dict[str, Dict[str, List[float]]]) -> Dict[str, float]:
        """Convert aggregated fuzzy outputs to crisp values"""
        outputs = {}
        
        for var_name, fuzzy_outputs in aggregated.items():
            # Compute center of gravity (centroid method)
            crisp_value = self._centroid_defuzzify(
                var_name,
                fuzzy_outputs
            )
            outputs[var_name] = crisp_value
            
        return outputs
        
    def _centroid_defuzzify(self, var_name: str, 
                           fuzzy_outputs: Dict[str, List[float]]) -> float:
        """Defuzzify using centroid method"""
        var = self.output_variables[var_name]
        
        # Discretize universe
        x = np.linspace(var.universe_min, var.universe_max, 100)
        
        # Compute aggregated membership function
        aggregated_membership = np.zeros_like(x)
        
        for set_name, firing_strengths in fuzzy_outputs.items():
            if not firing_strengths:
                continue
                
            # Maximum firing strength for this set
            max_strength = max(firing_strengths)
            
            # Clip membership function at firing strength
            fuzzy_set = var.fuzzy_sets[set_name]
            membership_values = np.array([fuzzy_set.membership(xi) for xi in x])
            clipped = np.minimum(membership_values, max_strength)
            
            # Take maximum (union)
            aggregated_membership = np.maximum(aggregated_membership, clipped)
            
        # Compute centroid
        if np.sum(aggregated_membership) == 0:
            # Default to midpoint if no rules fired
            return (var.universe_min + var.universe_max) / 2
            
        centroid = np.sum(x * aggregated_membership) / np.sum(aggregated_membership)
        
        return float(centroid)


# ============================================================================
# USAGE EXAMPLE: AGENT CAPABILITY ASSESSMENT
# ============================================================================

def create_agent_capability_system() -> FuzzyInferenceSystem:
    """Create fuzzy system for assessing agent task capability"""
    
    fis = FuzzyInferenceSystem()
    
    # Input 1: Task Complexity (0-100)
    fis.add_input_variable('complexity', 0, 100)
    fis.add_fuzzy_set_to_input('complexity', 'LOW', triangular(0, 0, 50))
    fis.add_fuzzy_set_to_input('complexity', 'MEDIUM', triangular(25, 50, 75))
    fis.add_fuzzy_set_to_input('complexity', 'HIGH', triangular(50, 100, 100))
    
    # Input 2: Agent Capability (0-100)
    fis.add_input_variable('capability', 0, 100)
    fis.add_fuzzy_set_to_input('capability', 'LOW', triangular(0, 0, 50))
    fis.add_fuzzy_set_to_input('capability', 'MEDIUM', triangular(25, 50, 75))
    fis.add_fuzzy_set_to_input('capability', 'HIGH', triangular(50, 100, 100))
    
    # Input 3: Agent Load (0-100)
    fis.add_input_variable('load', 0, 100)
    fis.add_fuzzy_set_to_input('load', 'LOW', triangular(0, 0, 50))
    fis.add_fuzzy_set_to_input('load', 'MEDIUM', triangular(25, 50, 75))
    fis.add_fuzzy_set_to_input('load', 'HIGH', triangular(50, 100, 100))
    
    # Output: Success Probability (0-100)
    fis.add_output_variable('success_prob', 0, 100)
    fis.add_fuzzy_set_to_output('success_prob', 'VERY_LOW', triangular(0, 0, 25))
    fis.add_fuzzy_set_to_output('success_prob', 'LOW', triangular(0, 25, 50))
    fis.add_fuzzy_set_to_output('success_prob', 'MEDIUM', triangular(25, 50, 75))
    fis.add_fuzzy_set_to_output('success_prob', 'HIGH', triangular(50, 75, 100))
    fis.add_fuzzy_set_to_output('success_prob', 'VERY_HIGH', triangular(75, 100, 100))
    
    # Define fuzzy rules
    fis.add_rule(
        [('complexity', 'LOW'), ('capability', 'HIGH'), ('load', 'LOW')],
        ('success_prob', 'VERY_HIGH'),
        weight=1.0
    )
    
    fis.add_rule(
        [('complexity', 'HIGH'), ('capability', 'LOW')],
        ('success_prob', 'VERY_LOW'),
        weight=1.0
    )
    
    fis.add_rule(
        [('complexity', 'MEDIUM'), ('capability', 'MEDIUM'), ('load', 'LOW')],
        ('success_prob', 'MEDIUM'),
        weight=0.9
    )
    
    fis.add_rule(
        [('load', 'HIGH')],
        ('success_prob', 'LOW'),
        weight=0.8
    )
    
    # Add more rules for comprehensive coverage...
    
    return fis


def example_fuzzy_inference():
    """Example usage of fuzzy inference"""
    fis = create_agent_capability_system()
    
    # Test case 1: Easy task, highly capable agent, low load
    result = fis.infer({
        'complexity': 20,
        'capability': 85,
        'load': 15
    })
    print(f"Success probability: {result['success_prob']:.1f}%")
    # Expected: ~90% (VERY_HIGH)
    
    # Test case 2: Hard task, moderately capable agent, high load
    result = fis.infer({
        'complexity': 80,
        'capability': 55,
        'load': 75
    })
    print(f"Success probability: {result['success_prob']:.1f}%")
    # Expected: ~30% (LOW)


# ============================================================================
# INTEGRATION WITH AGENT SYSTEM
# ============================================================================

class FuzzyAgent:
    """Agent with fuzzy logic reasoning"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.fis = create_agent_capability_system()
        self.current_load = 0.0
        self.capability_scores = {}
        
    def assess_task(self, task) -> Dict:
        """Assess if agent can handle task using fuzzy logic"""
        complexity = task.complexity_score * 100
        capability = self.get_capability_for_task(task) * 100
        load = self.current_load * 100
        
        result = self.fis.infer({
            'complexity': complexity,
            'capability': capability,
            'load': load
        })
        
        success_prob = result['success_prob'] / 100.0
        
        return {
            'can_handle': success_prob > 0.5,
            'success_probability': success_prob,
            'confidence': 'high' if success_prob > 0.7 else 'medium' if success_prob > 0.4 else 'low',
            'inputs': {
                'complexity': complexity,
                'capability': capability,
                'load': load
            }
        }
        
    def get_capability_for_task(self, task) -> float:
        """Get agent's capability score for task"""
        # Simplified - compute from capability scores
        if not task.required_capabilities:
            return 0.5
            
        scores = [
            self.capability_scores.get(cap, 0.5)
            for cap in task.required_capabilities
        ]
        
        return np.mean(scores)
```

This document continues with the remaining 19 critical gaps. Should I continue with the complete implementation of all gaps, or would you like me to create the reusable meta-prompt document first?


