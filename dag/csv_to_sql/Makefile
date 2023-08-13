
trigger:
	#direnv exec . bash -c "airflow dags trigger ${PWD##*/}"
	direnv exec . airflow dags trigger $(shell basename ${PWD})