WITH
    app
AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key([
            "u.last_name",
            "u.first_name",
            "u.email",
        ]) }} AS sk,
        u.last_name,
        u.first_name,
        u.email, 
        { user_id: u.id } AS __
    FROM
        {{ ref("staging__app__users") }} u
), 
    crm
AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key([
            "c.last_name",
            "c.first_name",
            "c.email",
        ]) }} AS sk,
        c.satisfaction_score,
        NULL AS __
    FROM
        {{ ref("staging__crm__customers") }} c
)
SELECT
    a.sk, 
    a.last_name,
    a.first_name,
    a.email,
    c.satisfaction_score,
    { app: a.__, crm: c.__ } AS __
FROM
    app a
LEFT JOIN
    crm c
ON
    c.sk = a.sk