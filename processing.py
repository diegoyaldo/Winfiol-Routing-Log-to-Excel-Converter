import re
import models
import pandas as pd
from tabulate import tabulate
import os

BR_VALUES = ["RA", "RO"]


def split_by_space_and_strip(line: str, one_or_more: bool) -> list[str]:
    if one_or_more:
        parts = re.split(r" +", line.strip())
    else:
        parts = re.split(r" {2,}", line.strip())
    return parts


def open_file(file_path: str) -> list[str]:
    with open(file_path, "r") as file:
        return file.readlines()


def get_logs_as_list(file_path: str) -> list[list[str]]:
    lines = open_file(file_path)
    beginning = []
    pattern1 = re.compile(r"( ) {4}00 {2}0$")
    pattern2 = re.compile(r"0\s+(\d+)\s+(\d+)\s+(\d+)$")
    for line in lines:
        if pattern1.search(line):
            line = pattern1.sub(
                lambda m: m.group(1).replace(" ", "~  ", 1) + "00  0", line
            )

        mtch = pattern2.search(line)
        if mtch:
            line = line[:mtch.start(0) + 5] + "~  " + line[mtch.start(0) + 10 :]
        beginning.append(line)

    sanitized = []
    for line in beginning:
        l = line.replace(":", " ")
        sanitized.append(l)

    ret = []
    for line in sanitized:
        split_by_more_than_one_space = "OLI OLI2" in line
        ret.append(split_by_space_and_strip(line, split_by_more_than_one_space))

    modified = []
    for line in ret:
        l = line[1:]
        modified.append(l)
    return modified


def is_new_route(log: list[str]) -> bool:
    return (
        "COT" in log and "EST" in log and "SI" in log and "ESS" in log and "ESR" in log
    )


def is_new_rc(log: list[str]) -> bool:
    return len(log) >= 2 and log[0].isnumeric() and (log[1] == "YES" or log[1] == "NO")


def has_br(log: list[str]) -> bool:
    for l in log:
        if "-" in l or "&" in l:
            return True
    return False


def assign_data(data, logs, i):
    i += 1  

    if logs[i][1] == "~":
        data.cot, data.si, data.ess, data.esr = (
            logs[i][0],
            logs[i][2],
            logs[i][3],
            logs[i][4],
        )
    else:
        data.cot, data.est, data.si, data.ess, data.esr, = (
            logs[i][0],
            logs[i][1],
            logs[i][2],
            logs[i][3],
            logs[i][4],
        )

    i += 2 
    if logs[i][0] != "~": 
        data.bnt = logs[i][0]
    ( data.rn, data.spr,) = ( logs[i][1], logs[i][2],)

    i += 2  
    data.isc = logs[i][0]
    if len(logs[i]) > 2:
        data.fcp = logs[i][1]
        data.d = logs[i][2]

    i += 1  
    return i


def process_logs(filepath):
    logs = get_logs_as_list(filepath)

    RCs: list[models.RC] = []
    for i in range(len(logs)):
        if is_new_rc(logs[i]):
            rc = models.RC(logs[i][0], None, [], [])
            if is_new_rc(logs[i]) and not has_br(logs[i]):
                rc.cch = logs[i][1]
            elif is_new_rc(logs[i]) and has_br(logs[i]):
                rc.br.append(logs[i][2])

            if is_new_rc(logs[i]) and is_new_route(logs[i]) and not has_br(logs[i]):
                data = models.Data()
                route = models.Routing(logs[i][2], logs[i][3])
                i = assign_data(data, logs, i)
                route.data = data
                rc.routing.append(route)
            # TODO: need to parse the rest of the BR here. 

            if has_br(logs[i]):
                if any(x in logs[i] for x in BR_VALUES):
                    print("TRUE")
                    rc.br.append(logs[i][2] + logs[i][3])
                else:
                    rc.br.append(logs[i][2])
                print(rc.br)

            # get the remaining routes
            while i < len(logs) and is_new_route(logs[i]) and not is_new_rc(logs[i]):
                data = models.Data()
                route = models.Routing(logs[i][0], logs[i][1])
                i = assign_data(data, logs, i)
                route.data = data
                rc.routing.append(route)

            RCs.append(rc)

    for rc in RCs:
        print(f"{rc.number} {rc.cch} {rc.br}")
        print("\t ROUTES")

        headers = [
            "TAG",
            "SP",
            "COT",
            "EST",
            "SI",
            "ESS",
            "ESR",
            "BNT",
            "RN",
            "SPR",
            "OLI",
            "OLI2",
            "ISC",
            "FCP",
            "D",
        ]
        table_data = []

        for route in rc.routing:
            table_data.append(
                [
                    route.tag,
                    route.sp,
                    route.data.cot,
                    route.data.est,
                    route.data.si,
                    route.data.ess,
                    route.data.esr,
                    route.data.bnt,
                    route.data.rn,
                    route.data.spr,
                    route.data.oli,
                    route.data.oli2,
                    route.data.isc,
                    route.data.fcp,
                    route.data.d,
                ]
            )

        # print the table
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    rc_dicts = []
    for rc in RCs:
        rc_dict = {
            "RC": rc.number,
            "CCH": rc.cch,
            "BR": " ".join(rc.br)
        }
        for route in rc.routing:
            route_dict = {
                "ROUTING": route.tag,
                "SP": route.sp,
                "COT": route.data.cot,
                "EST": route.data.est,
                "SI": route.data.si,
                "ESS": route.data.ess,
                "ESR": route.data.esr,
                "BNT": route.data.bnt,
                "RN": route.data.rn,
                "SPR": route.data.spr,
                "OLI": route.data.oli,
                "OLI2": route.data.oli2,
                "ISC": route.data.isc,
                "FCP": route.data.fcp,
                "D": route.data.d
            }
            combined_dict = {**rc_dict, **route_dict}
            rc_dicts.append(combined_dict)

    df = pd.DataFrame(rc_dicts)
    output_file = os.path.join('uploads', 'rcs.xlsx')
    df.to_excel(output_file, index=False)

    return 'rcs.xlsx'
