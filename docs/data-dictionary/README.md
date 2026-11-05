# Horisma data dictionary index

The current definition entry combines the immutable core and explicit versioned extensions:

- [Core project dictionary0.1.0](Horisma_Project_Data_Dictionary_EN.md): frozen P0 scientific definitions; its original bytes and manifest are unchanged.
- [Scientist identity, personal information and terminology extension0.2.0](Horisma_Scientist_Identity_and_Terminology_Extension_EN.md): candidate name forms, biography assertions, contextual mentions/coreference, citizenship/flag associations and term relations.
- [Person/name machine contract](../../spec/extensions/person_names.yaml) and [term relations](../../spec/extensions/term_aliases.yaml): extension codes and implementation scope.
- [Attribution events, mechanisms and book arguments0.1.0](Horisma_Attribution_Event_and_Mechanism_Extension_EN.md): proposed role-scoped contribution/credit anchors, provenance closure and causal-inference boundaries, with a [machine template](../../spec/extensions/attribution_event_template.yaml). This is a design extension, not an implemented historical adjudicator.

Candidate adapter conformance, source fidelity, identity qualification, semantic support and publication eligibility remain separate. An extension does not retroactively rewrite frozen evidence or create historical gold.
