# Limitations & Future Scope

## Current Phase 1 Limitations

### Infrastructure
- Single EC2 application host.
- No load balancer or auto scaling.
- No EKS/Kubernetes.
- No NAT Gateway.
- Budget-controlled RDS configuration.
- HTTPS/custom domain deferred.

### Retrieval and AI
- Active policy retrieval is deterministic keyword overlap.
- Embedding/FAISS components exist in the repository but are not the active retrieval path.
- Gemini explains supplied facts and policy context; it does not make the final lending decision.

### Document Intelligence
Current extraction depends on implemented document parsing and supported layouts. Complex scans and OCR-heavy documents may require stronger extraction.

### Testing
The project does not yet represent a production-scale performance/security test program.

## Decision Limitations
Configured financial rules are application/demo rules and are not presented as a real lender's underwriting policy.

The Review-Risk Score is a deterministic triage signal, not probability of default, credit score or AI prediction.

## Future Scope

### RAG
Move from keyword overlap to embedding/vector retrieval with evaluation of retrieval quality.

### Platform
- EKS/Kubernetes.
- ALB.
- Multiple replicas.
- Autoscaling.
- Stronger observability.
- Centralized logs, metrics and traces.

### Security
- HTTPS/custom domain.
- WAF.
- Secret rotation.
- Security scanning.
- Stronger network controls.

### CI/CD
- Build/publish immutable images.
- Automated deployment.
- Environment promotion.
- Approval gates.
- Rollback.
- Post-deployment validation.

### AI Governance
- Evaluation datasets.
- Retrieval evaluation.
- Prompt/version tracking.
- Structured-output validation.
- AI observability.
- Strong human-review controls.

### Document Intelligence
- OCR.
- Layout-aware extraction.
- Stronger entity matching.
- Anomaly/fraud detection as a separate controlled capability.

## Phase Boundary
Phase 1 demonstrates:

application → deterministic assessment → evidence → verification → policy context → grounded AI explanation → human advisor decision → audit trail → AWS deployment.

Phase 2 represents the path toward a more scalable production architecture and is not currently deployed.
