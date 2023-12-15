{{ config(
    alias="freelances",
) }}


SELECT
    b.sk, 
    b.last_name,
    b.first_name,
    b.email,
    b.satisfaction_score
FROM
    {{ ref("intermediate__base__freelances") }} b