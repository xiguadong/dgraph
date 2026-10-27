"""Renderable diagram catalog and the 65-figure lesson_2 coverage map."""

_QUESTIONS = {
    "block-definition": "Which types, blocks, and composition relationships make up the system?",
    "internal-block": "How are parts, ports, and connectors arranged inside a system?",
    "requirements": "How are requirements derived, satisfied, and verified?",
    "parametric": "Which constraints bind engineering parameters?",
    "use-case": "Which actors interact with which system goals?",
    "activity": "How do actions, decisions, and control flows proceed?",
    "sequence": "Which messages occur between lifelines, in what order?",
    "state-machine": "Which states and transitions define system behavior?",
    "package": "How is the model organized into packages and dependencies?",
    "sysml-v2": "How do views and viewpoints project a SysML v2 model?",
    "opm": "How do objects and processes form an OPM concept model?",
    "c4": "How do C4 zoom levels explain software architecture?",
    "context": "Where is the system boundary and which external interfaces cross it?",
    "ffbd": "How do functions flow, iterate, and run in parallel?",
    "n2": "Which interfaces connect system elements in a matrix?",
    "idef0": "Which inputs, outputs, controls, and mechanisms surround a function?",
    "dfd": "How does data move between processes, stores, and external entities?",
    "qfd": "How do customer needs map to engineering characteristics?",
    "tradespace": "Which alternatives dominate in the objective space?",
    "fta": "Which basic events combine into a top failure event?",
    "cld": "Which reinforcing and balancing feedback loops connect variables?",
    "sfd": "Which stocks, flows, and rates describe system dynamics?",
    "dodaf": "How do DoDAF viewpoints describe an enterprise architecture?",
    "ov1": "What is the operational concept and mission context?",
    "sv1": "Which systems and resource interfaces form the solution?",
    "cv2": "How are capabilities decomposed and related?",
    "arcadia": "How do ARCADIA layers move from operational analysis to EPBS?",
    "wbs": "How is project work decomposed into deliverable activities?",
    "pbs": "How is the product decomposed into physical elements?",
    "gantt": "Which tasks, dependencies, and milestones form the schedule?",
    "pert": "Which dependencies and paths determine project duration?",
    "risk-matrix": "How do probability and impact prioritize risks?",
    "burndown": "How does remaining work change across the iteration?",
    "class": "Which classes, features, and relationships describe software types?",
    "object": "Which instances and links form an object snapshot?",
    "component": "Which components and provided or required interfaces interact?",
    "composite-structure": "How are parts and connectors arranged inside a class?",
    "deployment": "Which artifacts and software instances run on which nodes?",
    "profile": "Which stereotypes extend a UML metamodel?",
    "communication": "Which interactions connect objects without a time axis?",
    "interaction-overview": "How are interaction fragments orchestrated?",
    "timing": "Which states and messages satisfy time constraints?",
    "event-storming": "How do events, commands, aggregates, and policies form a business narrative?",
    "impact-map": "How do goals connect actors, impacts, and deliverables?",
    "module-dependency": "Which modules depend on each other?",
    "class-hierarchy": "How do classes inherit and specialize?",
    "eta": "Which subsequent events follow an initiating event?",
    "kanban": "How does work flow across execution lanes and limits?",
    "bpmn": "How do participants, tasks, gateways, and events form a business process?",
    "archimate": "How do business, application, and technology layers relate?",
    "cicd": "Which checks, artifacts, gates, and deployments form delivery automation?",
    "deployment-topology": "Which networks, nodes, services, and links form runtime topology?",
    "flame-graph": "Which stack frames dominate execution time?",
    "call-graph": "Which functions call each other?",
    "story-map": "How do user activities, tasks, and releases organize stories?",
    "ddd-context-map": "How do bounded contexts and their relationships interact?",
    "dmn": "Which inputs and rules determine a decision output?",
    "er": "Which entities, attributes, and cardinalities describe data?",
    "c4-context": "Which people and external systems surround the software system?",
    "c4-container": "Which deployable containers form the software system?",
    "delivery": "How do source, builds, artifacts, storage, deployment, and runtime connect?",
}


def _entry(kind):
    return {"type": kind, "status": "renderable", "question": _QUESTIONS[kind], "schema": f"dgraph://schema/{kind}", "example": f"dgraph://example/{kind}"}


CATALOG = [_entry(kind) for kind in _QUESTIONS]


def _coverage(prefix, mapping):
    return [{"asset": f"02_ex_{prefix}_{asset}.svg", "type": kind} for asset, kind in mapping.items()]


LESSON_COVERAGE = (
    _coverage("sysml", {"bdd": "block-definition", "ibd": "internal-block", "req": "requirements", "par": "parametric", "uc": "use-case", "act": "activity", "sd": "sequence", "stm": "state-machine", "pkg": "package", "v2": "sysml-v2"})
    + _coverage("lang", {"opm": "opm", "c4": "c4"})
    + _coverage("se", {"context": "context", "ffbd": "ffbd", "n2": "n2", "idef0": "idef0", "dfd": "dfd", "qfd": "qfd", "tradespace": "tradespace", "fta": "fta", "cld": "cld", "sfd": "sfd"})
    + _coverage("fw", {"dodaf": "dodaf", "ov1": "ov1", "sv1": "sv1", "cv2": "cv2", "arcadia": "arcadia"})
    + _coverage("pm", {"wbs": "wbs", "pbs": "pbs", "gantt": "gantt", "pert": "pert", "risk": "risk-matrix", "burndown": "burndown"})
    + _coverage("uml", {"class": "class", "object": "object", "component": "component", "composite": "composite-structure", "deploy": "deployment", "pkg": "package", "profile": "profile", "usecase": "use-case", "activity": "activity", "state": "state-machine", "sequence": "sequence", "comm": "communication", "iov": "interaction-overview", "timing": "timing"})
    + _coverage("x", {"eventstorm": "event-storming", "impactmap": "impact-map", "moduledep": "module-dependency", "classhier": "class-hierarchy", "eta": "eta", "kanban": "kanban", "bpmn": "bpmn", "archimate": "archimate", "cicd": "cicd", "topology": "deployment-topology", "flame": "flame-graph", "callgraph": "call-graph", "storymap": "story-map", "ddd": "ddd-context-map", "dmn": "dmn", "er": "er", "c4_context": "c4-context", "c4_container": "c4-container"})
)
