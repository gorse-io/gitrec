/CREATE TABLE `\w+` \(/, /\) ENGINE=MyISAM DEFAULT CHARSET=latin1;/ {

    if ($0 ~ /CREATE TABLE/) {

        # Get table name
        table_name = substr($3, 2, length($3)-2)
        csv_name = output_folder table_name ".csv"

        # Clear column names
        delete column_names

    } else if ($0 ~ /ENGINE=MyISAM/) {

        # Print header
        header = ""
        for (i in column_names) {
            if (i > 1) {
                header = header ","
            }
            header = header column_names[i]
        }
        print header > csv_name

        # Print info
        print "Generating " csv_name " ..."

    } else if ($0 ~ /^\s+`\w+`/) {

        # Get column name
        column_name = substr($1, 2, length($1)-2)
        column_names[length(column_names)+1] = column_name

    }

}

/INSERT INTO `\w+` VALUES/ {

    # Get table name
    table_name = substr($3, 2, length($3)-2)
    csv_name = output_folder table_name ".csv"

    # Get fields
    $1 = $2 = $3 = $4 = ""
    split($0, fields, "),[(]")
    num_fields = length(fields)
    fields[1] = substr(fields[1], 6)
    fields[num_fields] = substr(fields[num_fields], 0, length(fields[num_fields])-2)

    # Print fields
    for (i in fields) {
        print fields[i] > csv_name
        # Count line
        count_line[table_name] += 1
    }
}

END {

    print "----------------------------------"
    printf("%10s Table\n", "Lines")
    print "----------------------------------"
    for (table_name in count_line) {
        printf("%10d %s\n", count_line[table_name], table_name)
    }
    print "----------------------------------"

}