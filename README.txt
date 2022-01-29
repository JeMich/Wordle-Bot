This is a pretty simple bot, so feel free to modify it any way that suits your purposes.

Wordle-Bot as-is can only work in one server and one channel at a time. This is subject to change when I feel like it and have a surplus of free time.

You must provide Wordle-Bot 2 files:
One is a token.txt that contains your bot token. You MUST keep this token secret, and if you're going to host your own version
of Wordle-Bot on git I strongly recommend keeping this file outside of the repository.

The other is a file called valid_solutions.csv which is a csv file that contains 1 valid wordle word per line. 
This allows you to build a custom wordle library if you want. The csv file included in the repo is the official wordle words.

Wordle-Bot knows the following commands:
!wb help, to show these commands
!wb hello, basically a ping for wordle bot
!wb custom ||word||, to start a custom, unverified word
!wb verified ||word||, to start a custom, verified word (verified meaning present in the csv)
!wb random, to let wordle-bot choose a verified word
!wb quit, to stop a game in progress and reveal the word.