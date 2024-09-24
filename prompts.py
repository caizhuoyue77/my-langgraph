"""A file containing prompts definition."""

GRAPH_EXTRACTION_PROMPT = """
-Goal-
Given a text document that is API documenatation and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.
 
-Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)
 
2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
 Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_strength>)
 
3. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.
 
4. When finished, output {completion_delimiter}
 
######################
-Examples-
######################
Example 1:
Entity_types: ORGANIZATION,PERSON
Text:
The Verdantis's Central Institution is scheduled to meet on Monday and Thursday, with the institution planning to release its latest policy decision on Thursday at 1:30 p.m. PDT, followed by a press conference where Central Institution Chair Martin Smith will take questions. Investors expect the Market Strategy Committee to hold its benchmark interest rate steady in a range of 3.5%-3.75%.
######################
Output:
("entity"{tuple_delimiter}CENTRAL INSTITUTION{tuple_delimiter}ORGANIZATION{tuple_delimiter}The Central Institution is the Federal Reserve of Verdantis, which is setting interest rates on Monday and Thursday)
{record_delimiter}
("entity"{tuple_delimiter}MARTIN SMITH{tuple_delimiter}PERSON{tuple_delimiter}Martin Smith is the chair of the Central Institution)
{record_delimiter}
("entity"{tuple_delimiter}MARKET STRATEGY COMMITTEE{tuple_delimiter}ORGANIZATION{tuple_delimiter}The Central Institution committee makes key decisions about interest rates and the growth of Verdantis's money supply)
{record_delimiter}
("relationship"{tuple_delimiter}MARTIN SMITH{tuple_delimiter}CENTRAL INSTITUTION{tuple_delimiter}Martin Smith is the Chair of the Central Institution and will answer questions at a press conference{tuple_delimiter}9)
{completion_delimiter}

######################
Example 2:
Entity_types: ORGANIZATION
Text:
TechGlobal's (TG) stock skyrocketed in its opening day on the Global Exchange Thursday. But IPO experts warn that the semiconductor corporation's debut on the public markets isn't indicative of how other newly listed companies may perform.

TechGlobal, a formerly public company, was taken private by Vision Holdings in 2014. The well-established chip designer says it powers 85% of premium smartphones.
######################
Output:
("entity"{tuple_delimiter}TECHGLOBAL{tuple_delimiter}ORGANIZATION{tuple_delimiter}TechGlobal is a stock now listed on the Global Exchange which powers 85% of premium smartphones)
{record_delimiter}
("entity"{tuple_delimiter}VISION HOLDINGS{tuple_delimiter}ORGANIZATION{tuple_delimiter}Vision Holdings is a firm that previously owned TechGlobal)
{record_delimiter}
("relationship"{tuple_delimiter}TECHGLOBAL{tuple_delimiter}VISION HOLDINGS{tuple_delimiter}Vision Holdings formerly owned TechGlobal from 2014 until present{tuple_delimiter}5)
{completion_delimiter}

######################

NOTE: YOU SHOULD ONLY GIVE THE OUTPUT AND NOTHING ELSE. THE MORE NODES AND MORE EDGES, THE BETTER.

######################
-Real Data-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:"""

CONTINUE_PROMPT = "MANY entities and relationships were missed in the last extraction. Remember to ONLY emit entities that match any of the previously extracted types. Add them below using the same format:\n"
LOOP_PROMPT = "It appears some entities and relationships may have still been missed.  Answer YES | NO if there are still entities or relationships that need to be added.\n"