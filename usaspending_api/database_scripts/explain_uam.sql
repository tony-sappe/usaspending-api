DROP MATERIALIZED VIEW IF EXISTS uam_explain_test;

EXPLAIN (ANALYZE, VERBOSE, COSTS, BUFFERS, FORMAT JSON)
CREATE MATERIALIZED VIEW uam_explain_test AS
SELECT
  to_tsvector(CONCAT_WS(' ',
    COALESCE(recipient_lookup.recipient_name, legal_entity.recipient_name),
    contract_data.naics,
    contract_data.naics_description,
    psc.description,
    (SELECT string_agg(tn.description, ' ') FROM transaction_normalized AS tn WHERE tn.award_id = awards.id GROUP BY tn.award_id)
  )) AS keyword_ts_vector,
  to_tsvector(CONCAT_WS(' ', awards.piid, awards.fain, awards.uri)) AS award_ts_vector,
  to_tsvector(COALESCE(recipient_lookup.recipient_name, legal_entity.recipient_name)) AS recipient_name_ts_vector,

  awards.id AS award_id,
  awards.category,
  awards.type,
  awards.type_description,
  awards.piid,
  awards.fain,
  awards.uri,
  awards.total_obligation,
  awards.description,
  obligation_to_enum(awards.total_obligation) AS total_obl_bin,
  awards.total_subsidy_cost,
  awards.total_loan_value,

  awards.recipient_id,
  UPPER(COALESCE(recipient_lookup.recipient_name, legal_entity.recipient_name)) AS recipient_name,
  legal_entity.recipient_unique_id AS recipient_unique_id,
  legal_entity.parent_recipient_unique_id,
  legal_entity.business_categories,

  latest_transaction.action_date,
  latest_transaction.fiscal_year,
  latest_transaction.last_modified_date,
  awards.period_of_performance_start_date,
  awards.period_of_performance_current_end_date,
  awards.date_signed,

  transaction_fabs.original_loan_subsidy_cost,
  transaction_fabs.face_value_loan_guarantee,

  latest_transaction.awarding_agency_id,
  latest_transaction.funding_agency_id,
  TAA.name AS awarding_toptier_agency_name,
  TFA.name AS funding_toptier_agency_name,
  SAA.name AS awarding_subtier_agency_name,
  SFA.name AS funding_subtier_agency_name,
  TAA.cgac_code AS awarding_toptier_agency_code,
  TFA.cgac_code AS funding_toptier_agency_code,
  SAA.subtier_code AS awarding_subtier_agency_code,
  SFA.subtier_code AS funding_subtier_agency_code,

  COALESCE(contract_data.legal_entity_country_code, transaction_fabs.legal_entity_country_code) AS recipient_location_country_code,
  COALESCE(contract_data.legal_entity_country_name, transaction_fabs.legal_entity_country_name) AS recipient_location_country_name,
  COALESCE(contract_data.legal_entity_state_code, transaction_fabs.legal_entity_state_code) AS recipient_location_state_code,
  COALESCE(contract_data.legal_entity_county_code, transaction_fabs.legal_entity_county_code) AS recipient_location_county_code,
  COALESCE(contract_data.legal_entity_county_name, transaction_fabs.legal_entity_county_name) AS recipient_location_county_name,
  COALESCE(contract_data.legal_entity_congressional, transaction_fabs.legal_entity_congressional) AS recipient_location_congressional_code,
  COALESCE(contract_data.legal_entity_zip5, transaction_fabs.legal_entity_zip5) AS recipient_location_zip5,

  place_of_performance.country_name AS pop_country_name,
  place_of_performance.location_country_code AS pop_country_code,
  place_of_performance.state_code AS pop_state_code,
  place_of_performance.county_code AS pop_county_code,
  place_of_performance.county_name AS pop_county_name,
  place_of_performance.city_code AS pop_city_code,
  place_of_performance.zip5 AS pop_zip5,
  place_of_performance.congressional_code AS pop_congressional_code,

  transaction_fabs.cfda_number,
  transaction_fabs.sai_number,
  contract_data.pulled_from,
  contract_data.type_of_contract_pricing,
  contract_data.extent_competed,
  contract_data.type_set_aside,

  contract_data.product_or_service_code,
  psc.description AS product_or_service_description,
  contract_data.naics AS naics_code,
  contract_data.naics_description
FROM
  awards
INNER JOIN
  transaction_normalized AS latest_transaction
    ON (awards.latest_transaction_id = latest_transaction.id)
LEFT OUTER JOIN
  transaction_fabs
    ON (awards.latest_transaction_id = transaction_fabs.transaction_id)
LEFT OUTER JOIN
  transaction_fpds AS contract_data
    ON (awards.latest_transaction_id = contract_data.transaction_id)
INNER JOIN
  legal_entity
    ON (awards.recipient_id = legal_entity.legal_entity_id)
LEFT OUTER JOIN
  (SELECT
    recipient_hash,
    legal_business_name AS recipient_name,
    duns
  FROM recipient_lookup AS rlv
  ) recipient_lookup ON recipient_lookup.duns = legal_entity.recipient_unique_id AND legal_entity.recipient_unique_id IS NOT NULL
LEFT OUTER JOIN
  references_location AS place_of_performance ON (awards.place_of_performance_id = place_of_performance.location_id)
LEFT OUTER JOIN
  psc ON (contract_data.product_or_service_code = psc.code)
LEFT OUTER JOIN
  agency AS AA
    ON (awards.awarding_agency_id = AA.id)
LEFT OUTER JOIN
  toptier_agency AS TAA
    ON (AA.toptier_agency_id = TAA.toptier_agency_id)
LEFT OUTER JOIN
  subtier_agency AS SAA
    ON (AA.subtier_agency_id = SAA.subtier_agency_id)
LEFT OUTER JOIN
  agency AS FA ON (awards.funding_agency_id = FA.id)
LEFT OUTER JOIN
  toptier_agency AS TFA
    ON (FA.toptier_agency_id = TFA.toptier_agency_id)
LEFT OUTER JOIN
  subtier_agency AS SFA
    ON (FA.subtier_agency_id = SFA.subtier_agency_id)
WHERE
  (awards.category IS NOT NULL OR contract_data.pulled_from = 'IDV') AND
  latest_transaction.action_date >= '2000-10-01'
ORDER BY
  awards.total_obligation DESC NULLS LAST;