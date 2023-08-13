{%- for row in ti.xcom_pull('transform_to_update_query') %}
UPDATE my_table
    name = '{{ row.new_name }}'
WHERE
    id = {{ row.id }};
{%- endfor %}