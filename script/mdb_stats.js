/*
 helpful commands for reporting
*/

// number of bets by expert
db.bets.aggregate([{$group: { _id:"$author", count: {$sum:1}}}])

// number of bets by date-crawled
db.bets.aggregate([{$group: { _id:"$crawled-date", count: {$sum:1}}}])
