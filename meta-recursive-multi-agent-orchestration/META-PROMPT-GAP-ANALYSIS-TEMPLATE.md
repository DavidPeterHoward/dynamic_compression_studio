# Meta-Prompt: Comprehensive Gap Analysis Template
## Reusable Framework for Multi-Dimensional Specification Review

---

## PURPOSE

This document provides a **reusable meta-prompt** that can be used to conduct comprehensive gap analyses on any technical specification, documentation suite, or system design. It has been refined based on successful application to a 25,000+ line AI system specification.

**Use this prompt when you need to:**
- Identify missing components in technical documentation
- Assess completeness across multiple dimensions
- Prioritize implementation work
- Prepare specifications for production deployment
- Ensure LLM-comprehensible documentation
- Find blind spots in system design

---

## THE META-PROMPT

### Version 1: Comprehensive (Recommended for Large Projects)

```
PROJECT CONTEXT:
[Provide brief description of project, its goals, and current documentation state]

TASK:
Conduct a comprehensive multi-dimensional gap analysis of the provided documentation/specification 
to identify missing components, inconsistencies, and areas requiring additional detail for 
production-ready implementation.

ANALYTICAL DIMENSIONS:
Analyze across the following 7 independent dimensions:

1. LOGICAL COMPLETENESS
   - Assess coverage of logical systems (classical and non-classical)
   - Identify missing reasoning frameworks
   - Check for logical consistency and completeness
   - Evaluate formal specifications

2. RHETORICAL & COMMUNICATION
   - Evaluate communication patterns and protocols
   - Assess semantic clarity and precision
   - Check for ambiguity and misinterpretation risks
   - Examine discourse structure

3. SEMANTIC & ONTOLOGICAL
   - Review knowledge representation frameworks
   - Assess ontology completeness and rigor
   - Check for semantic gaps and inconsistencies
   - Evaluate concept definitions

4. IMPLEMENTATION PRAGMATICS
   - Identify missing implementation patterns
   - Assess error handling and resilience
   - Check for scalability considerations
   - Evaluate operational readiness

5. SAFETY & ETHICS
   - Review safety mechanisms and monitors
   - Assess ethical frameworks
   - Check for bias and fairness considerations
   - Evaluate risk mitigation strategies

6. HUMAN-SYSTEM INTERACTION
   - Assess user experience considerations
   - Review trust and transparency mechanisms
   - Check for cognitive load management
   - Evaluate feedback systems

7. META-COGNITIVE & EPISTEMOLOGICAL
   - Review self-awareness mechanisms
   - Assess learning and adaptation frameworks
   - Check for confidence calibration
   - Evaluate meta-reasoning capabilities

OUTPUT REQUIREMENTS:
For each dimension, provide:

A. Current Coverage Assessment
   - What exists: List present components
   - Rating: Score out of 10 with justification
   - Strengths: What is well-covered

B. Critical Gap Identification
   - Gap Title: Clear, specific name
   - Description: What is missing and why it matters
   - Priority: CRITICAL / HIGH / MEDIUM / LOW
   - Impact: Effect on system if not addressed
   - Effort: Estimated person-weeks to implement
   - Code Example: Pseudocode showing what's needed (minimum 50 lines)

C. Gap Summary Table
   | Aspect | Status | Priority | Difficulty | Lines of Code |
   |--------|--------|----------|------------|---------------|

CROSS-DIMENSIONAL ANALYSIS:
After individual dimension reviews, provide:

1. Gap Categorization Matrix
   - Count gaps by dimension and priority
   - Identify interdependencies between gaps
   - Create dependency graph

2. Coverage Heat Map
   - Visual representation of coverage by dimension
   - Overall percentage coverage
   - Identify weakest areas

3. Prioritized Recommendations
   - Phase 1 (Critical): Must-have for viability
   - Phase 2 (High): Significant value additions
   - Phase 3 (Medium): Nice-to-have enhancements
   - Include timeline and resource requirements

4. Final Assessment
   - Summary statistics (total gaps, by priority)
   - Most critical missing elements (top 10)
   - Overall assessment and recommendations
   - Risk assessment (with gaps vs. without gaps)

DELIVERABLE FORMAT:
- Structured markdown document
- Minimum 1,500 lines of analysis
- Include 20+ code examples (50-200 lines each)
- Provide actionable implementation guidance
- Use academic rigor in analysis
```

---

### Version 2: Focused (For Smaller Projects or Specific Concerns)

```
PROJECT: [Project name and brief description]

ANALYSIS SCOPE:
Focus on the following specific dimensions:
- [ ] Logical & Reasoning Systems
- [ ] Communication Protocols
- [ ] Safety & Ethics
- [ ] Implementation Patterns
- [ ] User Experience
- [ ] Testing & Validation
- [X] [Custom dimension]

FOR EACH SELECTED DIMENSION:

1. What currently exists? (List all present components)

2. What is missing? (Identify gaps with priority: CRITICAL/HIGH/MEDIUM/LOW)

3. Why does each gap matter? (Impact if not addressed)

4. How to implement? (50-100 lines of pseudocode per gap)

5. What are the dependencies? (What must be built first)

OUTPUT REQUIREMENTS:
- Gap analysis document (500+ lines)
- Prioritized recommendation list
- Implementation effort estimates
- Risk assessment

SPECIFIC FOCUS AREAS:
[List any particular concerns, e.g., "Focus on production readiness" or 
 "Emphasize AI safety" or "Prioritize user experience"]
```

---

### Version 3: Quick Assessment (For Rapid Reviews)

```
Review the provided [specification/documentation/system design] and identify:

1. TOP 10 CRITICAL GAPS
   For each gap:
   - Name and brief description
   - Why it's critical
   - Estimated effort to address
   - Code example showing what's needed (30-50 lines)

2. COVERAGE ASSESSMENT
   Rate completeness (0-100%) for:
   - Logical foundations
   - Implementation details
   - Safety mechanisms
   - User experience
   - Testing approach
   - Overall: [weighted average]

3. IMMEDIATE RECOMMENDATIONS
   What must be added before this can be:
   - Used for development?
   - Deployed to staging?
   - Released to production?

4. RISK SUMMARY
   - Highest risk areas (top 5)
   - Consequences if gaps not addressed
   - Recommended next steps

DELIVERABLE: 200-500 line analysis document
```

---

## USAGE EXAMPLES

### Example 1: AI System Documentation Review

```
PROJECT CONTEXT:
Multi-agent orchestration system with 25,000 lines of documentation covering 
architecture, algorithms, mathematics, and implementation guidelines. Intended 
for LLM-based development and production deployment.

TASK:
[Use Version 1: Comprehensive prompt above]

SPECIFIC CONCERNS:
- System will modify its own code (self-improvement)
- Must be safe for production use
- Will interact with non-technical users
- Needs to handle uncertain and contradictory information
```

### Example 2: API Specification Review

```
PROJECT: RESTful API for financial transactions

ANALYSIS SCOPE:
[Use Version 2: Focused prompt]
- [X] Safety & Ethics (data privacy, financial regulations)
- [X] Implementation Patterns (error handling, rate limiting)
- [X] Testing & Validation
- [ ] Logical & Reasoning Systems (not applicable)

SPECIFIC FOCUS AREAS:
- GDPR compliance
- PCI DSS requirements
- Fraud detection mechanisms
- Audit trail completeness
```

### Example 3: Quick Review Before Implementation

```
[Use Version 3: Quick Assessment prompt]

Context: Microservice architecture specification for e-commerce platform.
Team is ready to start implementation next week. Need quick gap check.

Focus on: What will block implementation if not addressed?
```

---

## PROMPT CUSTOMIZATION GUIDE

### For Different Project Types

**Software Systems:**
```
Add dimensions:
- Scalability & Performance
- Security & Compliance
- Deployment & Operations
- Data Management
```

**AI/ML Systems:**
```
Add dimensions:
- Model Selection & Training
- Bias & Fairness
- Explainability & Transparency
- Continuous Learning
```

**Hardware Systems:**
```
Add dimensions:
- Physical Constraints
- Power & Thermal Management
- Manufacturing Considerations
- Failure Modes & Reliability
```

**Business Processes:**
```
Add dimensions:
- Stakeholder Alignment
- Change Management
- Metrics & KPIs
- Regulatory Compliance
```

### For Different Audiences

**For Technical Teams:**
- Emphasize implementation details
- Include code examples (100+ lines)
- Focus on architecture and patterns
- Provide complexity analysis

**For Management:**
- Emphasize business impact
- Include resource requirements
- Focus on risks and ROI
- Provide timeline estimates

**For Researchers:**
- Emphasize theoretical foundations
- Include formal specifications
- Focus on novel contributions
- Provide literature references

**For Compliance/Legal:**
- Emphasize regulations and standards
- Include compliance checklists
- Focus on audit trail and documentation
- Provide risk assessments

### For Different Project Stages

**Early Design (Conceptual):**
```
Emphasize:
- Logical completeness
- Architectural soundness
- Feasibility assessment
- Alternative approaches
```

**Mid-Development (Implementation):**
```
Emphasize:
- Implementation patterns
- Error handling
- Testing strategies
- Integration points
```

**Pre-Production (Deployment):**
```
Emphasize:
- Safety mechanisms
- Monitoring & observability
- Resilience patterns
- Operational runbooks
```

**Post-Launch (Maintenance):**
```
Emphasize:
- Evolution pathways
- Technical debt
- Scalability limits
- User feedback incorporation
```

---

## QUALITY CHECKLIST

Use this checklist to ensure your gap analysis is comprehensive:

### Coverage Checks
- [ ] All specified dimensions analyzed independently
- [ ] Each dimension has coverage assessment (X/10 rating)
- [ ] Gaps identified across all priority levels (not just critical)
- [ ] Code examples provided for major gaps (50+ lines each)
- [ ] Interdependencies between gaps documented

### Depth Checks
- [ ] Each gap has clear description (what, why, how)
- [ ] Impact analysis provided (consequences if not addressed)
- [ ] Effort estimates included (person-weeks)
- [ ] Implementation guidance provided (pseudocode)
- [ ] Testing approach suggested

### Actionability Checks
- [ ] Gaps prioritized (CRITICAL/HIGH/MEDIUM/LOW)
- [ ] Phased implementation roadmap provided
- [ ] Resource requirements specified
- [ ] Timeline estimates included
- [ ] Dependencies clearly mapped

### Completeness Checks
- [ ] Gap categorization matrix included
- [ ] Coverage heat map provided
- [ ] Summary statistics calculated
- [ ] Risk assessment included
- [ ] Recommendations prioritized

### Quality Checks
- [ ] Analysis is specific (not generic observations)
- [ ] Examples are relevant to project domain
- [ ] Recommendations are actionable
- [ ] Document is well-structured
- [ ] Minimum length requirements met

---

## EXPECTED OUTPUTS

### Minimum Deliverables

**For Comprehensive Analysis:**
- Main analysis document: 1,500+ lines
- Gap categorization matrix
- Coverage heat map
- Prioritized recommendations (3 phases)
- Implementation guide for critical gaps (500+ lines)
- Total: ~2,000 lines of documentation

**For Focused Analysis:**
- Main analysis document: 500+ lines
- Gap summary table
- Priority recommendations
- Implementation examples
- Total: ~700 lines of documentation

**For Quick Assessment:**
- Analysis summary: 200-500 lines
- Top 10 critical gaps
- Coverage scores
- Immediate recommendations
- Total: ~300 lines minimum

### Quality Metrics

**Good Gap Analysis Has:**
- ✅ 20+ distinct gaps identified
- ✅ Coverage <70% indicates thoroughness
- ✅ Multiple priority levels (not all "critical")
- ✅ Specific code examples (not hand-waving)
- ✅ Actionable recommendations
- ✅ Resource/time estimates
- ✅ Clear prioritization

**Warning Signs:**
- ⚠️ <10 gaps identified (likely too shallow)
- ⚠️ All gaps marked "critical" (poor prioritization)
- ⚠️ No code examples (not actionable)
- ⚠️ Generic observations (not project-specific)
- ⚠️ No effort estimates (not useful for planning)
- ⚠️ Coverage >90% (probably missed things)

---

## ADVANCED TECHNIQUES

### Multi-Pass Analysis

**Pass 1: Breadth**
- Quick scan across all dimensions
- Identify obvious gaps
- Create initial gap list
- Time: 2-4 hours

**Pass 2: Depth**
- Deep dive into each dimension
- Detailed gap analysis
- Code examples and specifications
- Time: 8-16 hours

**Pass 3: Integration**
- Cross-dimensional analysis
- Dependency mapping
- Priority calibration
- Effort estimation
- Time: 4-8 hours

**Total: 14-28 hours for comprehensive analysis**

### Automated Assistance

Use LLMs to accelerate analysis:

```
For each dimension:
1. Extract all relevant sections from documentation
2. Feed to LLM with dimension-specific prompt
3. Review LLM output critically
4. Augment with human expertise
5. Synthesize findings

Estimated speedup: 2-3x faster than pure manual analysis
```

### Collaborative Review

**Team-Based Approach:**
- Assign 1-2 dimensions per team member
- Each conducts independent analysis
- Group synthesis meeting to integrate
- Resolve conflicting assessments
- Finalize prioritization collaboratively

**Benefits:**
- Broader perspective
- Catches more gaps
- Better effort estimates
- Increased buy-in

### Iterative Refinement

**Iteration 1:** Quick assessment (Version 3)
- Identify major gaps
- Decide if full analysis needed
- Time: 2-4 hours

**Iteration 2:** Focused analysis (Version 2)
- Deep dive on critical areas
- Detailed recommendations
- Time: 8-12 hours

**Iteration 3:** Comprehensive review (Version 1)
- Full multi-dimensional analysis
- Complete implementation guide
- Time: 16-24 hours

**Total: 26-40 hours across all iterations**

---

## TEMPLATE VARIANTS

### For Documentation Review

```
Analyze the provided documentation suite for:

1. LOGICAL CONSISTENCY
   - Internal contradictions
   - Ambiguous specifications
   - Missing definitions
   - Incomplete explanations

2. IMPLEMENTATION READINESS
   - Sufficient detail for coding?
   - Clear algorithms specified?
   - Edge cases covered?
   - Error handling defined?

3. COMPLETENESS
   - All components specified?
   - All interactions documented?
   - All data structures defined?
   - All APIs documented?

4. TESTABILITY
   - Clear success criteria?
   - Test cases suggested?
   - Validation methods specified?
   - Performance targets defined?

Output: Gap analysis focusing on documentation quality
```

### For Architecture Review

```
Evaluate the system architecture for:

1. SCALABILITY
   - Bottlenecks identified?
   - Horizontal scaling approach?
   - Load balancing strategy?
   - Resource management?

2. RESILIENCE
   - Failure modes addressed?
   - Recovery mechanisms?
   - Circuit breakers?
   - Fallback strategies?

3. SECURITY
   - Authentication/authorization?
   - Data encryption?
   - Input validation?
   - Audit logging?

4. OBSERVABILITY
   - Monitoring strategy?
   - Logging framework?
   - Tracing approach?
   - Alerting rules?

Output: Architectural gap analysis with remediation guidance
```

### For Requirements Review

```
Assess the requirements specification for:

1. COMPLETENESS
   - All functional requirements?
   - All non-functional requirements?
   - All constraints specified?
   - All assumptions documented?

2. CLARITY
   - Unambiguous language?
   - Measurable criteria?
   - Testable specifications?
   - Clear priorities?

3. CONSISTENCY
   - No conflicts between requirements?
   - Aligned with goals?
   - Compatible constraints?
   - Coherent priorities?

4. FEASIBILITY
   - Technically possible?
   - Resource-realistic?
   - Timeline-achievable?
   - Cost-appropriate?

Output: Requirements gap analysis with refinement suggestions
```

---

## CUSTOMIZATION PARAMETERS

### Adjustable Dimensions

**Depth Level:**
- `SURFACE`: High-level overview only
- `STANDARD`: Normal depth (recommended)
- `DEEP`: Exhaustive analysis with proofs

**Priority Threshold:**
- `CRITICAL_ONLY`: Only showstopping gaps
- `HIGH_AND_ABOVE`: Critical + High priority
- `ALL`: Every gap found (can be overwhelming)

**Code Example Detail:**
- `MINIMAL`: 20-30 lines, key concepts only
- `STANDARD`: 50-100 lines, working examples
- `COMPLETE`: 200+ lines, production-ready code

**Domain Focus:**
```python
domain_weights = {
    'logical': 0.2,        # Adjust 0.0-1.0
    'rhetorical': 0.1,
    'semantic': 0.15,
    'implementation': 0.25,
    'safety': 0.15,
    'human_ai': 0.1,
    'meta_cognitive': 0.05
}
# Higher weight = more emphasis in analysis
```

---

## SUCCESS METRICS

### How to Measure Effectiveness

**Immediate (Analysis Quality):**
- Number of gaps identified: >20 for large projects
- Coverage across all dimensions: <75% indicates thoroughness
- Code examples provided: >10 detailed examples
- Actionable recommendations: >80% have clear next steps

**Short-term (Implementation):**
- Percentage of gaps addressed: Track over time
- Implementation velocity: Gaps per sprint
- Re-work required: <10% indicates good analysis

**Long-term (System Quality):**
- Production incidents: Related to identified gaps?
- User satisfaction: Improved after addressing UX gaps?
- Maintainability: Did gap fixes reduce technical debt?
- Safety record: No incidents related to safety gaps?

---

## FINAL RECOMMENDATIONS

### When to Use This Meta-Prompt

**Always Use For:**
- Pre-production readiness reviews
- Large documentation suites (>5,000 lines)
- Safety-critical systems
- AI/ML systems that learn or self-modify
- Projects with >10 person-year effort

**Consider Using For:**
- Mid-project architecture reviews
- Post-implementation audits
- Acquisition due diligence
- Compliance assessments
- Knowledge transfer documentation

**Probably Overkill For:**
- Simple utilities or scripts
- Proof-of-concept prototypes
- Throwaway code
- Well-established patterns (CRUD apps)
- Projects <1 person-month

### Best Practices

1. **Start Early**: Gap analysis during design is 10x cheaper than during maintenance

2. **Be Specific**: "Missing error handling" → "No circuit breaker for external API calls"

3. **Provide Examples**: Every major gap should have 50+ lines of implementation code

4. **Prioritize Ruthlessly**: Not everything is critical. Be honest about priority.

5. **Estimate Effort**: "2 person-weeks" is more useful than "medium effort"

6. **Consider Dependencies**: Some gaps must be fixed before others

7. **Think Production**: What will break at 3am on a Saturday?

8. **Iterate**: First pass misses things. Review your analysis.

9. **Get Feedback**: Have domain experts review findings

10. **Track Progress**: Gap analysis is worthless without follow-through

---

## VERSION HISTORY

- **v1.0** (2025-10-30): Initial release based on 25,000-line AI system analysis
- **v1.1** (Future): Refinements based on usage feedback

---

## LICENSE & ATTRIBUTION

This meta-prompt is released under MIT License for free use.

**Attribution:** Based on comprehensive gap analysis of Meta-Recursive Multi-Agent Orchestration System (October 2025)

**Citation:**
```
Meta-Prompt: Comprehensive Gap Analysis Template
Source: Meta-Recursive Multi-Agent Orchestration Project
Date: 2025-10-30
Dimensions: 7 (Logical, Rhetorical, Semantic, Implementation, Safety, Human-AI, Meta-Cognitive)
```

---

**USE THIS TEMPLATE TO ENSURE YOUR SPECIFICATIONS ARE PRODUCTION-READY** ✅

