CREATE VIEW
  de_flat
AS
 SELECT
   DataElement.*,
   DataElementConcept.preferredName AS dec_preferredName,
   DataElementConcept.preferredDefinition AS dec_preferredDefinition,
   DataElementConcept.longName AS dec_longName,
   DataElementConcept.context AS dec_context,

   
   ObjectClass.preferredName AS oc_preferredName,
   ObjectClass.preferredDefinition AS oc_preferredDefinition,
   ObjectClass.longName AS oc_longName,
   ObjectClass.context AS oc_context,

   ClassConcept.conceptCode AS cc_conceptCode,
   ClassConcept.longName AS cc_longName,
   ClassConcept.definition AS cc_definition,
   ClassConcept.primaryIndicator AS cc_primaryIndicator,

   Property.preferredName AS p_preferredName,
   Property.preferredDefinition AS p_preferredDefinition,
   Property.longName AS p_longName,
   Property.context AS p_context,

   PropertyConcept.conceptCode AS pc_conceptCode,
   PropertyConcept.longName AS pc_longName,
   PropertyConcept.definition AS pc_definition,
   PropertyConcept.primaryIndicator AS pc_primaryIndicator

 FROM
   DataElement
   
   INNER JOIN DataElementConcept ON (DataElement.DataElementConcept_uid = DataElementConcept.uid)

   INNER JOIN ObjectClass ON (DataElementConcept.ObjectClass_uid = ObjectClass.uid)
   INNER JOIN ObjectClass_Concepts ON (ObjectClass.uid = ObjectClass_Concepts.ObjectClass_uid)
   INNER JOIN Concept AS ClassConcept ON (ObjectClass_Concepts.Concepts_id = ClassConcept.id)

   INNER JOIN Property ON (DataElementConcept.Property_uid = Property.uid)
   INNER JOIN Property_Concepts ON (Property.uid = Property_Concepts.Property_uid)
   INNER JOIN Concept AS PropertyConcept ON (Property_Concepts.Concepts_id = PropertyConcept.id);

CREATE VIEW
  de_flat_slim
AS
 SELECT
   preferredName,
   longName,
   context,
   dec_preferredName,
   dec_longName,
   dec_context,
   
   oc_preferredName,
   oc_longName,
   oc_context,

   cc_conceptCode,
   cc_longName,
   cc_primaryIndicator,

   p_preferredName,
   p_longName,
   p_context,

   pc_conceptCode,
   pc_longName,
   pc_primaryIndicator

 FROM
   de_flat;

CREATE VIEW
  de_flat_slim_primary
AS
 SELECT
  *
 FROM
  de_flat_slim
 WHERE
  cc_primaryIndicator = "Yes" AND pc_primaryIndicator = "Yes";



CREATE VIEW
  dce_flat
AS
 SELECT
   DataElementConcept.*,
   
   ObjectClass.preferredName AS oc_preferredName,
   ObjectClass.preferredDefinition AS oc_preferredDefinition,
   ObjectClass.longName AS oc_longName,
   ObjectClass.context AS oc_context,

   ClassConcept.conceptCode AS cc_conceptCode,
   ClassConcept.longName AS cc_longName,
   ClassConcept.definition AS cc_definition,
   ClassConcept.primaryIndicator AS cc_primaryIndicator,

   Property.preferredName AS p_preferredName,
   Property.preferredDefinition AS p_preferredDefinition,
   Property.longName AS p_longName,
   Property.context AS p_context,

   PropertyConcept.conceptCode AS pc_conceptCode,
   PropertyConcept.longName AS pc_longName,
   PropertyConcept.definition AS pc_definition,
   PropertyConcept.primaryIndicator AS pc_primaryIndicator

 FROM
   DataElementConcept

   INNER JOIN ObjectClass ON (DataElementConcept.ObjectClass_uid = ObjectClass.uid)
   INNER JOIN ObjectClass_Concepts ON (ObjectClass.uid = ObjectClass_Concepts.ObjectClass_uid)
   INNER JOIN Concept AS ClassConcept ON (ObjectClass_Concepts.Concepts_id = ClassConcept.id)

   INNER JOIN Property ON (DataElementConcept.Property_uid = Property.uid)
   INNER JOIN Property_Concepts ON (Property.uid = Property_Concepts.Property_uid)
   INNER JOIN Concept AS PropertyConcept ON (Property_Concepts.Concepts_id = PropertyConcept.id);

