/*
 this file is not a script.
 Contains only helper commands for setting up a mongodb database
*/

// index for fast inserting new records (upserting)
db.bets.createIndex({author:1, date:1, factor:1, match:1, stake:1, type:1, status:1})

// mark the most interesting experts
db.experts.updateMany(
    {"expert":{
        "$in":['chaplygin', 'falcao1984', 'teplofevralya', 'nvaluev', 'ostapbender', 'karpovvyacheslav', 'netsenko', 'zhukov']}
    },
    {"$set":{top:true}})
