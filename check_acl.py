def checkACLID(teamID: str):
    if int(teamID) > 0x4000 and int(teamID) <= 0xC000:  # from ACL eFootball to ACL PES
        return str(int(teamID) + 65536 - 16384)  # + PES 21 ACL OFFSET - eF ACL OFFSET
    elif int(teamID) > 0x14000:
        return str(int(teamID) - 0x14000)
    # elif (
    #     int(teamID) > 0xC000 and int(teamID) <= 0x10000
    # ):  # dismiss Asian Comp1 (in case we needed to do another tests)
    #     return 0
    else:
        return teamID


# 0x4000  # 16384
# 0xC000  # 49152
# 0x10000  # 65536
# 0x10000 - 0x4000  # 49152
