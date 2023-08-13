SELECT
*
FROM
my_table
WHERE
id in (
{%- for r in ti.xcom_pull('extract_csv') %}
    {%- if loop.first %}
    {{ r.id }}
    {%- else %}
    ,{{ r.id }}
    {%- endif %}
{%- endfor %}
)