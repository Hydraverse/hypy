import requests
import argparse
import pprint
from collections.abc import Iterable
from collections import namedtuple

from hydra.util.struct import dictuple


_DEFAULTS = {
    str: '""',
    int: 0,
    float: 0.0,
    list: []
}


def _DFL(v, t):
    return t(v) if v is not None else _DEFAULTS.get(t, None)


class HydraRPC:
    host: str = "127.0.0.1"
    port: int = 3389
    user: str = ""
    # noinspection HardcodedPassword
    password: str = ""
    url: str = ""
    __session = None
    __json = False

    class Error(BaseException):
        response: requests.Response = None
        error: namedtuple = None

        def __init__(self, response):
            self.response = response
            self.error = dictuple("error", response.json()["error"]) if len(response.content) else None

        def __str__(self) -> str:
            return str(self.error) if self.error is not None else str(self.response)

        def __repr__(self) -> str:
            return repr(self.error) if self.error is not None else repr(self.response)

    def __init__(self, host: str = host, port: int = port, user: str = user, password: str = password, json=False):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.__json = json

        userpass = f"{user}{':'+password if len(password) else ''}@" if user else ""

        # noinspection HttpUrlsUsage
        self.url = f"http://{userpass}{host}:{port}/"

    @staticmethod
    def __parser__(parser: argparse.ArgumentParser, require=False):
        parser.add_argument("-H", "--host", default=HydraRPC.host, type=str, help="rpc host", required=require)
        parser.add_argument("-p", "--port", default=HydraRPC.port, type=int, help="rpc port", required=False)
        parser.add_argument("-u", "--user", default=HydraRPC.user, type=str, help="rpc user", required=False)
        parser.add_argument("-P", "--password", default=HydraRPC.password, type=str, help="rpc password", required=False)
        parser.add_argument("-j", "--json", action="store_true", default=False, help="output parseable json", required=False)
        # TODO: Maybe add URL spec string as another entry method

    @staticmethod
    def __from_parsed__(args: argparse.Namespace):
        return HydraRPC(args.host, args.port, args.user, args.password, args.json)

    @staticmethod
    def __make_request_dict(name: str, *args) -> dict:
        # q = lambda a: f'"{str(a)}"'
        return {
            "id": 1,
            "jsonrpc": "2.0",
            "method": name,
            "params": [
                (_DFL(arg[1], arg[0])) if isinstance(arg, tuple) else (
                    arg if (isinstance(arg, (str, int, float)) or not isinstance(arg, Iterable))
                    else f"[{','.join(a for a in arg)}]"
                )
                for arg in filter(lambda arg: arg is not None, args)
            ]
        }

    def __call(self, name: str, *args):
        if self.__session is None:
            self.__session = requests.Session()

        rsp: requests.Response = self.__session.post(url=self.url, json=HydraRPC.__make_request_dict(name, *args))

        if not rsp.ok:
            raise HydraRPC.Error(rsp)
        else:
            result = rsp.json()["result"]
            return \
                dictuple(name, result) if (isinstance(result, dict) and not self.__json) else (
                    result if self.__json else (
                        [dictuple(f"{name}_{i}", item) for i, item in enumerate(result)] if isinstance(result, list) else str(result)
                    )
                )

    def __string__(self, result, indent=0, indent_amt=4):
        q = lambda s: f'"{s}"' if isinstance(s, str) else str(s)

        if isinstance(result, (str, int, float)):
            return str(result)

        if self.__json:
            return pprint.pformat(result._asdict() if hasattr(result, "_asdict") else result)

        if isinstance(result, list):
            return ",\n".join(self.__string__(item) for item in result)

        return \
            (indent * indent_amt) * " " + \
            f"{type(result).__name__}\n{(indent * indent_amt) * ' '}{{\n" + \
            ",\n".join(
                self.__string__(value, indent + 1, indent_amt)
                if hasattr(value, "_asdict")
                else ((indent + 1) * indent_amt) * " " + f"""{name}: {q(value) or _DEFAULTS.get(type(value), str)}"""
                for (name, value) in (result._asdict() if hasattr(result, "_asdict") else result).items()
            ) + \
            f"\n{(indent * indent_amt) * ' '}}}"

    # == Blockchain ==

    def callcontract(self, address: str, data: str, sender_address: str = None, gas_limit: int = None):
        if gas_limit is not None and sender_address is None:
            sender_address = ""

        return self.__call("callcontract", (str, address), (str, data), (str, sender_address), (int, gas_limit))

    def getaccountinfo(self, address: str): return self.__call("getaccountinfo", (str, address))

    def getbestblockhash(self): return self.__call("getbestblockhash")

    def getblock(self, blockhash: str, verbosity: int = None):
        return self.__call("getaccountinfo", (str, blockhash), (int, verbosity))

    def getblockchaininfo(self): return self.__call("getblockchaininfo")

    def getblockcount(self): return self.__call("getblockcount")

    def getblockhash(self, height: int): return self.__call("getblockhash", (int, height))

    # TODO: Typing on all params from here down

    def getblockheader(self, blockhash, verbose=None): return self.__call("getblockheader", blockhash, verbose)

    def getblockstats(self, hash_or_height, stats=None): return self.__call("getblockstats", hash_or_height, stats)

    def getchaintips(self): return self.__call("getchaintips")

    def getchaintxstats(self, nblocks=None, blockhash=None): return self.__call("getchaintxstats", nblocks, blockhash)

    def getcontractcode(self, address): return self.__call("getcontractcode", address)

    def getdifficulty(self): return self.__call("getdifficulty")

    def getestimatedannualroi(self): return self.__call("getestimatedannualroi")

    def getmempoolancestors(self, txid, verbose=None): return self.__call("getmempoolancestors", txid, verbose)

    def getmempooldescendants(self, txid, verbose=None): return self.__call("getmempooldescendants", txid, verbose)

    def getmempoolentry(self, txid): return self.__call("getmempoolentry", txid)

    def getmempoolinfo(self): return self.__call("getmempoolinfo")

    def getrawmempool(self, verbose=None): return self.__call("getrawmempool", verbose)

    def getstorage(self, address, block_num=None, index=None):
        return self.__call("getstorage", address, block_num, index)

    def gettransactionreceipt(self, hash_): return self.__call("gettransactionreceipt", hash_)

    def gettxout(self, txid, n, include_mempool=None): return self.__call("gettxout", txid, n, include_mempool)

    def gettxoutproof(self, txid_list, blockhash=None):
        if isinstance(txid_list, str):
            txid_list = (txid_list,)

        return self.__call("gettxoutproof", txid_list, blockhash)

    def gettxoutsetinfo(self): return self.__call("gettxoutsetinfo")

    def listcontracts(self, start=None, display=None): return self.__call("listcontracts", start, display)

    def preciousblock(self, blockhash): return self.__call("preciousblock", blockhash)

    def pruneblockchain(self, height): return self.__call("pruneblockchain", height)

    def savemempool(self, height): return self.__call("savemempool", height)

    def scantxoutset(self, action, scanobjects_list):
        if isinstance(scanobjects_list, str):
            scanobjects_list = (scanobjects_list,)
        return self.__call("scantxoutset", action, scanobjects_list)

    def searchlogs(self, from_block, to_block, address=None, topics=None, minconf=None):
        return self.__call("searchlogs", from_block, to_block, address, topics, minconf)

    def verifychain(self, checklevel=None, nblocks=None): return self.__call("verifychain", checklevel, nblocks)

    def verifytxoutproof(self, proof): return self.__call("verifytxoutproof", proof)

    def waitforlogs(self, from_block=None, to_block=None, filter_=None, minconf=None):
        return self.__call("waitforlogs", from_block, to_block, filter_, minconf)

    # == Control ==

    def getdgpinfo(self): return self.__call("getdgpinfo")

    def getinfo(self): return self.__call("getinfo")

    def getmemoryinfo(self, mode=None): return self.__call("getmemoryinfo", mode)

    def getoracleinfo(self): return self.__call("getoracleinfo")

    def getrpcinfo(self): return self.__call("getrpcinfo")

    def help(self, command=None): return self.__call("help", command)

    def logging(self, include_category_list=None, exclude_category_list=None):
        return self.__call("logging", include_category_list, exclude_category_list)

    def stop(self): return self.__call("stop")

    def uptime(self): return self.__call("uptime")

    # == Generating ==

    def generate(self, nblocks, maxtries=None): return self.__call("generate", nblocks, maxtries)

    def generatetoaddress(self, nblocks, address, maxtries=None):
        return self.__call("generatetoaddress", nblocks, address, maxtries)

    # == Mining ==

    def getblocktemplate(self, template_request): return self.__call("getblocktemplate", template_request)

    def getmininginfo(self): return self.__call("getmininginfo")

    def getnetworkhashps(self, nblocks=None, height=None): return self.__call("getnetworkhashps", nblocks, height)

    def getstakinginfo(self): return self.__call("getstakinginfo")

    def submitblock(self, hexdata, dummy=None): return self.__call("submitblock", hexdata, dummy)

    def submitheader(self, hexdata): return self.__call("submitheader", hexdata)

    # == Network ==

    def addnode(self, node, command): return self.__call("addnode", node, command)

    def clearbanned(self): return self.__call("clearbanned")

    def disconnectnode(self, address=None, nodeid=None): return self.__call("disconnectnode", address, nodeid)

    def getaddednodeinfo(self, node=None): return self.__call("getaddednodeinfo", node)

    def getconnectioncount(self): return self.__call("getconnectioncount")

    def getnettotals(self): return self.__call("getnettotals")

    def getnetworkinfo(self): return self.__call("getnetworkinfo")

    def getnodeaddresses(self, count: int = None): return self.__call("getnodeaddresses", (int, count))

    def getpeerinfo(self): return self.__call("getpeerinfo")

    def listbanned(self): return self.__call("listbanned")

    def ping(self): return self.__call("ping")

    def setban(self, subnet, command, bantime=None, absolute=None):
        return self.__call("setban", subnet, command, bantime, absolute)

    def setnetworkactive(self, state): return self.__call("setnetworkactive", state)

    # == Rawtransactions ==

    def decoderawtransaction(self, hexstring, iswitness=None):
        return self.__call("decoderawtransaction", hexstring, iswitness)

    def fromhexaddress(self, hexaddress): return self.__call("fromhexaddress", hexaddress)

    def gethexaddress(self, address): return self.__call("gethexaddress", address)

    def getrawtransaction(self, txid, verbose=None, blockhash=None):
        return self.__call("getrawtransaction", txid, verbose, blockhash)

    # == Util ==

    def createmultisig(self, nrequired, key_list, address_type=None):
        return self.__call("createmultisig", nrequired, key_list, address_type)

    def deriveaddresses(self, descriptor, range_=None):
        return self.__call("deriveaddresses", descriptor, range_)

    def estimatesmartfee(self, conf_target, estimate_mode=None):
        return self.__call("estimatesmartfee", conf_target, estimate_mode)

    def getdescriptorinfo(self, descriptor): return self.__call("getdescriptorinfo", descriptor)

    def signmessagewithprivatekey(self, privkey, message):
        return self.__call("signmessagewithprivatekey", privkey, message)

    def validateaddress(self, address): return self.__call("validateaddress", address)

    def verifymessage(self, address, signature, message):
        return self.__call("verifymessage", address, signature, message)

    # == Wallet ==

    def addmultisigaddress(self, nrequired, key_list, label=None, address_type=None):
        if address_type is not None and label is None:
            label = ''
        return self.__call("addmultisigaddress", nrequired, key_list, label, address_type)

    def backupwallet(self, destination): return self.__call("backupwallet", destination)

    def craetecontract(self, bytecode, gas_limit, senderaddress=None, broadcast=None, change_to_sender=None):
        return self.__call("craetecontract", bytecode, gas_limit, senderaddress, broadcast, change_to_sender)

    def createwallet(self, wallet_name, disable_private_keys=None, blank=None):
        return self.__call("createwallet", wallet_name, disable_private_keys, blank)

    def dumpprivkey(self, address): return self.__call("dumpprivkey", address)

    def dumpwallet(self, filename): return self.__call("dumpwallet", filename)

    def encryptwallet(self, passphrase): return self.__call("encryptwallet", passphrase)

    def getaddressesbylabel(self, label=""): return self.__call("getaddressesbylabel", label)

    def getaddressinfo(self, address): return self.__call("getaddressinfo", address)

    def getbalance(self, dummy=None, minconf=None, include_watchonly=None):
        return self.__call("getbalance", dummy, minconf, include_watchonly)

    def getbalanceofaddress(self, address): return self.__call("getbalanceofaddress", address)

    def getnewaddress(self, label="", address_type=None): return self.__call("getnewaddress", label, address_type)

    def getrawchangeaddress(self, address_type=None): return self.__call("getrawchangeaddress", address_type)

    def getreceivedbyaddress(self, address, minconf=None): return self.__call("getreceivedbyaddress", address, minconf)

    def getreceivedbylabel(self, label="", minconf=None): return self.__call("getreceivedbylabel", label, minconf)

    def gettransaction(self, txid, include_watchonly=None, waitconf=None):
        return self.__call("gettransaction", txid, include_watchonly, waitconf)

    def getunconfirmedbalance(self): return self.__call("getunconfirmedbalance")

    def getwalletinfo(self): return self.__call("getwalletinfo")

    def importaddress(self, address, label=None, rescan=None, p2sh=None):
        if rescan is not None and label is None:
            label = ""
        return self.__call("importaddress", address, label, rescan, p2sh)

    def importmulti(self, requests_, options=None): return self.__call("importmulti", requests_, options)

    def importprivkey(self, hydraprivkey, label="", rescan=None):
        return self.__call("importprivkey", hydraprivkey, label, rescan)

    def importprunedfunds(self, rawtransaction, txoutproof):
        return self.__call("importprunedfunds", rawtransaction, txoutproof)

    def importpubkey(self, pubkey, label="", rescan=None): return self.__call("importpubkey", pubkey, label, rescan)

    def importwallet(self, filename): return self.__call("importwallet", filename)

    def keypoolrefill(self, newsize=None): return self.__call("keypoolrefill", newsize)

    def listaddressgroupings(self): return self.__call("listaddressgroupings")

    def listlabels(self, purpose=None): return self.__call("listlabels", purpose)

    def listlockunspent(self): return self.__call("listlockunspent")

    def listreceivedbyaddress(self, minconf=None, include_empty=None, include_watchonly=None, address_filter=None):
        return self.__call("listreceivedbyaddress", minconf, include_empty, include_watchonly, address_filter)

    def listreceivedbylabel(self, minconf=None, include_empty=None, include_watchonly=None):
        return self.__call("listreceivedbylabel", minconf, include_empty, include_watchonly)

    def listsinceblock(self, blockhash, target_confirmations=None, include_watchonly=None, include_removed=None):
        return self.__call("listsinceblock", blockhash, target_confirmations, include_watchonly, include_removed)

    def listtransactions(self, label="", count=None, skip=None, include_watchonly=None):
        return self.__call("listtransactions", label, count, skip, include_watchonly)

    def listunspent(self, minconf=None, maxconf=None, address_list=None, include_unsafe=None, query_options=None):
        return self.__call("listunspent", minconf, maxconf, address_list, include_unsafe, query_options)

    def listwalletdir(self): return self.__call("listwalletdir")

    def listwallets(self): return self.__call("listwallets")

    def loadwallet(self, filename): return self.__call("loadwallet", filename)

    def lockunspent(self, unlock, txid_vout_list=None): return self.__call("lockunspent", unlock, txid_vout_list)

    def removeprunedfunds(self, txid): return self.__call("removeprunedfunds", txid)

    def rescanblockchain(self, start_height=None, stop_height=None):
        return self.__call("rescanblockchain", start_height, stop_height)

    def reservebalance(self, reserve=None, amount=None): return self.__call("reservebalance", reserve, amount)

    def sendtoaddress(self, address, amount, comment="", comment_to="", subtractfeefromamount="false",
                      replaceable="false", conf_target="null", estimate_mode="", senderaddress="",
                      change_to_sender="false"):
        return self.__call("sendtoaddress", address, amount, comment, comment_to, subtractfeefromamount, replaceable,
                           conf_target, estimate_mode, senderaddress, change_to_sender)

    def sendtocontract(self, contractaddress, datahex, amount=0, gas_limit=250000, senderaddress="", broadcast="true",
                       change_to_sender="false"):
        return self.__call("sendtocontract", contractaddress, datahex, amount, gas_limit, senderaddress, broadcast,
                           change_to_sender)

    def sethdseed(self, newkeypool=None, seed=None): return self.__call("sethdseed", newkeypool, seed)

    def setlabel(self, address, label): return self.__call("setlabel", address, label)

    def settxfee(self, amount): return self.__call("settxfee", amount)

    def signmessage(self, address, message): return self.__call("signmessage", address, message)

    def signrawsendertransactionwithwallet(self, hexstring, sighashtype=None):
        return self.__call("signrawsendertransactionwithwallet", hexstring, sighashtype)

    def signrawtransactionwithwallet(self, hexstring, txid_entry_list, sighashtype=None):
        return self.__call("signrawtransactionwithwallet", hexstring, txid_entry_list, sighashtype)

    def unloadwallet(self, wallet_name=None): return self.__call("unloadwallet", wallet_name)

    def walletlock(self): return self.__call("walletlock")

    def walletpassphrase(self, passphrase, timeout, staking_only=None):
        return self.__call("walletpassphrase", passphrase, timeout, staking_only)

    def walletpassphrasechange(self, oldpassphrase, newpassphrase):
        return self.__call("walletpassphrasechange", oldpassphrase, newpassphrase)
