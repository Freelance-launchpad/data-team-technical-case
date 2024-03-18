SELECT
    {{ dbt_utils.generate_surrogate_key([
        "f.sk",
        "jc.start_date",
    ]) }} AS sk,
    f.sk AS freelancer_sk,
    jc.start_date,
    jc.end_date,
    jc.entity,
    { app: { job_contract_id: jc.id } } AS __
FROM
    {{ ref("staging__app__job_contracts") }} jc
LEFT JOIN
    {{ ref("intermediate__base__freelancers") }} f
ON
    f.__.app.user_id = jc.user_id