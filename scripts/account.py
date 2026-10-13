#[=============]#
# ACCOUNT CLASS #
#[=============]#
class Account:
    def __init__(self,stats,username,password,level):
        self.stats = stats
        self.level = level
        self.username = username
        self.password = password

    # Updating Statistics
    def updateStats(self):
        file = open(f"accounts/{self.username}.txt","w")
        file.write(f"[USERNAME]: {self.username}\n[PASSWORD]: {self.password}\n[STATS]:\n    [no. jumps]: {self.stats["no. jumps"]}\n    [total score]: {self.stats["total score"]}\n    [no. deaths]: {self.stats["no. deaths"]}\n[LEVEL]:\n")
        tempFile = open("scripts/levels/temp.txt")
        for line in tempFile.readlines():
            file.write(str(line))
        tempFile.close()
        file.close()