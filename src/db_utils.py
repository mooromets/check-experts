# coding=utf-8

import pymongo
import logging

DB_CONN = "mongodb://localhost:27017/"
DB_NAME = "br"
COL_EXPERTS = "experts"
COL_BETS = "bets"


def upsert_experts(experts):
    #open collection
    myclient = pymongo.MongoClient(DB_CONN)
    mydb = myclient[DB_NAME]
    mycol = mydb[COL_EXPERTS]

    #process experts
    for one in experts:
        logging.info('Upserting author: %s', one)
        res = mycol.update({'expert':one}, {"$setOnInsert": {'expert':one}}, upsert=True)
        logging.info(res)


def insert_untracked_bets(bets):
    #open collection
    myclient = pymongo.MongoClient(DB_CONN)
    mydb = myclient[DB_NAME]
    mycol = mydb[COL_BETS]

    #process bets
    for bet in bets:
        logging.debug(bet)
        res = mycol.update(
            {
                "author": bet["author"],
                'date': bet['date'],
                'factor': bet['factor'],
                'match': bet['match'],
                'stake': bet['stake'],
                'type': bet['type'],
            },
            {"$setOnInsert": bet},
            upsert=True)
        #TODO remove hardcoded field names
        logging.debug(res)

def if_expert_exists(name):
    #open collection
    myclient = pymongo.MongoClient(DB_CONN)
    mydb = myclient[DB_NAME]
    mycol = mydb[COL_EXPERTS]
    res = mycol.find({"expert":name}).count() > 0
    logging.info("Expert:%s's presence in DB:%s", name, res)
    return res
