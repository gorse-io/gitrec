# Steam SQL file
STEAM_SQL_FILE	= /path/to/steam.sql

# Data directories
OUTPUT_CSV_DIR 	= /path/to/dataset/
STEAM_FULL_DIR 	= ${OUTPUT_CSV_DIR}steam-full/

# CSV files
APP_CSV_FILE	= ${STEAM_FULL_DIR}App_ID_Info.csv
DEV_CSV_FILE	= ${STEAM_FULL_DIR}Games_Developers.csv
PUB_CSV_FILE	= ${STEAM_FULL_DIR}Games_Publishers.csv
USER_CSV_FILE	= ${STEAM_FULL_DIR}Player_Summaries.csv
GAME_CSV_FILE	= ${STEAM_FULL_DIR}Games_2.csv
GENRES_CSV_FILE	= ${STEAM_FULL_DIR}Games_Genres.csv
CSV_FILES		= ${APP_CSV_FILE} ${DEV_CSV_FILE} ${PUB_CSV_FILE} ${USER_CSV_FILE} \
				  ${GAME_CSV_FILE} ${Games_Genres} ${GENRES_CSV_FILE}

${CSV_FILES}:
	# convert SQL file to csv files
	mkdir -p ${STEAM_FULL_DIR}
	awk -f parse.awk output_folder=${STEAM_FULL_DIR} ${STEAM_SQL_FILE}

csv: ${CSV_FILES}

100k: ${CSV_FILES}
	# create steam 100k dataset
	mkdir -p ${OUTPUT_CSV_DIR}steam-100k
	sed '1d' ${USER_CSV_FILE} | shuf -n 15000 > ${OUTPUT_CSV_DIR}steam-100k/users.csv
	python3 sample.py ${STEAM_FULL_DIR} ${OUTPUT_CSV_DIR}steam-100k/users.csv

1m: ${CSV_FILES}
	# create steam 1m dataset
	mkdir -p ${OUTPUT_CSV_DIR}steam-1m
	sed '1d' ${USER_CSV_FILE} | shuf -n 150000 > ${OUTPUT_CSV_DIR}steam-1m/users.csv
	python3 sample.py ${STEAM_FULL_DIR} ${OUTPUT_CSV_DIR}steam-1m/users.csv

10m: ${CSV_FILES}
	# create steam 10m dataset
	mkdir -p ${OUTPUT_CSV_DIR}steam-10m
	sed '1d' ${USER_CSV_FILE} | shuf -n 1500000 > ${OUTPUT_CSV_DIR}steam-10m/users.csv
	python3 sample.py ${STEAM_FULL_DIR} ${OUTPUT_CSV_DIR}steam-10m/users.csv
