import os
import requests
import argparse
import pprint
import json
from collections import namedtuple
from urllib.parse import urlsplit, urlunsplit

from hydra.util.struct import dictuple


_DEFAULTS = {
    str: '""',
    int: 0,
    float: 0.0,
    list: [],
    bool: False
}


class HydraRPC:
    url: str = f"test://127.0.0.1"
    __session = None
    __json = False

    MAINNET_PORT = 3389
    TESTNET_PORT = 13389

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

    def __init__(self, url: str = url, json_=False):
        self.__json = json_
        self.__mainnet, self.url = HydraRPC.__parse_url__(url) if not isinstance(url, tuple) else url

    @staticmethod
    def __parse_url__(url: str):
        url_split = urlsplit(url)

        schemes_hydra = ("mainnet", "main", "testnet", "test")
        schemes_main = ("http", "mainnet", "main")
        schemes = schemes_main + ("testnet", "test")

        if url_split.scheme not in schemes:
            raise ValueError(f"Invalid scheme for url: {url}")

        netloc = str(url_split.netloc)

        port = url_split.port

        if port is None:
            port = HydraRPC.MAINNET_PORT if url_split.scheme in schemes_main else HydraRPC.TESTNET_PORT
            netloc += f":{port}"
            mainnet = port == HydraRPC.MAINNET_PORT
        elif url_split.scheme not in schemes_hydra:
            raise ValueError("hydra scheme required when specifying port number")
        else:
            mainnet = url_split.scheme in schemes_main

        return mainnet, urlunsplit((
            "http",
            netloc,
            url_split.path,
            url_split.query,
            url_split.fragment
        ))

    @staticmethod
    def __parse_param__(param: str):
        try:
            return json.loads(param)
        except json.decoder.JSONDecodeError:
            try:
                return json.loads(f'"{param}"')
            except json.decoder.JSONDecodeError:
                raise

    @staticmethod
    def __parser__(parser: argparse.ArgumentParser, require=False, allow_json=True):

        parser.add_argument("-r", "--rpc", default=os.environ.get("HY_RPC", HydraRPC.url), type=str,
                            help="rpc url (env: HY_RPC)", required=require)

        if allow_json:
            parser.add_argument("-j", "--json", action="store_true", default=False, help="output parseable json",
                                required=False)

    @staticmethod
    def __from_parsed__(args: argparse.Namespace):
        return HydraRPC(url=HydraRPC.__parse_url__(args.rpc), json_=getattr(args, "json", False))

    @staticmethod
    def __make_request_dict(name: str, *args) -> dict:
        # q = lambda a: f'"{str(a)}"'
        return {
            "id": 1,
            "jsonrpc": "2.0",
            "method": name,
            "params": list(filter(lambda arg: arg is not None, args))
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
                        [
                            (
                                dictuple(f"{name}_{i}", item) if isinstance(item, dict)
                                else item
                            )
                            for i, item in enumerate(result)
                        ] if isinstance(result, list)
                        else result
                    )
                )

    @staticmethod
    def __asdict__(result):

        if isinstance(result, (list, tuple)):
            return list(map(HydraRPC.__asdict__, result))

        if not hasattr(result, "_asdict"):
            return result

        return dict(map(lambda kv: (kv[0], HydraRPC.__asdict__(kv[1])), result._asdict().items()))

    @property
    def mainnet(self):
        return self.__mainnet

    def __string__(self, result, indent=0, indent_amt=4):
        q = lambda s: f'"{s}"' if isinstance(s, str) else str(s)

        if result is None:
            return ""

        if isinstance(result, (str, int, float)):
            return str(result or _DEFAULTS.get(type(result), _DEFAULTS[str]))

        if self.__json:
            return pprint.pformat(HydraRPC.__asdict__(result))

        if isinstance(result, list):
            return ",\n".join(self.__string__(item) for item in result)

        return \
            (indent * indent_amt) * " " + \
            f"{type(result).__name__}\n{(indent * indent_amt) * ' '}{{\n" + \
            ",\n".join(
                self.__string__(value, indent + 1, indent_amt)
                if hasattr(value, "_asdict")
                else ((indent + 1) * indent_amt) * " " + f"""{name}: {value or _DEFAULTS.get(type(value), _DEFAULTS[str])}"""
                for (name, value) in (result._asdict() if hasattr(result, "_asdict") else (result if isinstance(result, dict) else {"result": result})).items()
            ) + \
            f"\n{(indent * indent_amt) * ' '}}}"

    # == Blockchain ==

    def callcontract(self, address: str, data: str, sender_address: str = None, gas_limit: int = None):
        if gas_limit is not None and sender_address is None:
            sender_address = ""

        return self.__call("callcontract", address, data, sender_address, gas_limit)

    def getaccountinfo(self, address: str): return self.__call("getaccountinfo", address)

    def getbestblockhash(self): return self.__call("getbestblockhash")

    def getblock(self, blockhash: str, verbosity: int = None):
        return self.__call("getblock", blockhash, verbosity)

    def getblockchaininfo(self): return self.__call("getblockchaininfo")

    def getblockcount(self): return self.__call("getblockcount")

    def getblockhash(self, height: int): return self.__call("getblockhash", height)

    def getblockheader(self, blockhash: str, verbose: bool = None):
        return self.__call("getblockheader", blockhash, verbose)

    def getblockstats(self, hash_or_height: (int, str), stats: (list, tuple) = None):
        return self.__call("getblockstats", hash_or_height, stats)

    def getchaintips(self): return self.__call("getchaintips")

    def getchaintxstats(self, nblocks: int = None, blockhash: str = None):
        return self.__call("getchaintxstats", nblocks, blockhash)

    def getcontractcode(self, address: str): return self.__call("getcontractcode", address)

    def getdifficulty(self): return self.__call("getdifficulty")

    def getestimatedannualroi(self): return self.__call("getestimatedannualroi")

    def getmempoolancestors(self, txid: str, verbose: bool = None): return self.__call("getmempoolancestors", txid, verbose)

    def getmempooldescendants(self, txid: str, verbose: bool = None): return self.__call("getmempooldescendants", txid, verbose)

    def getmempoolentry(self, txid: str): return self.__call("getmempoolentry", txid)

    def getmempoolinfo(self): return self.__call("getmempoolinfo")

    def getrawmempool(self, verbose: bool = None): return self.__call("getrawmempool", verbose)

    def getstorage(self, address: str, block_num: int = None, index: int = None):
        return self.__call("getstorage", address, block_num, index)

    def gettransactionreceipt(self, hash_: str): return self.__call("gettransactionreceipt", hash_)

    def gettxout(self, txid: str, n: int, include_mempool: bool = None):
        return self.__call("gettxout", txid, n, include_mempool)

    def gettxoutproof(self, txid_list: (list, tuple), blockhash: str = None):
        if isinstance(txid_list, str):
            txid_list = (txid_list,)

        return self.__call("gettxoutproof", txid_list, blockhash)

    def gettxoutsetinfo(self): return self.__call("gettxoutsetinfo")

    def listcontracts(self, start: int = None, max_display: int = None):
        return self.__call("listcontracts", start, max_display)

    def preciousblock(self, blockhash: str): return self.__call("preciousblock", blockhash)

    def pruneblockchain(self, height: int): return self.__call("pruneblockchain", height)

    def savemempool(self, height: int): return self.__call("savemempool", height)

    def scantxoutset(self, action: str, scanobjects_list: (list, tuple)):
        if isinstance(scanobjects_list, str):
            scanobjects_list = (scanobjects_list,)
        return self.__call("scantxoutset", action, scanobjects_list)

    def searchlogs(self, from_block: int, to_block: int, address: str = None, topics: (list, tuple) = None,
                   minconf: int = None):
        return self.__call("searchlogs", from_block, to_block, address, topics, minconf)

    def verifychain(self, checklevel: int = None, nblocks: int = None): return self.__call("verifychain", checklevel, nblocks)

    def verifytxoutproof(self, proof: str): return self.__call("verifytxoutproof", proof)

    def waitforlogs(self, from_block: int = None, to_block: int = None, filter_: str = None, minconf: int = None):
        return self.__call("waitforlogs", from_block, to_block, filter_, minconf)

    # == Control ==

    def getdgpinfo(self): return self.__call("getdgpinfo")

    def getinfo(self): return self.__call("getinfo")

    def getmemoryinfo(self, mode: str = None): return self.__call("getmemoryinfo", mode)

    def getoracleinfo(self): return self.__call("getoracleinfo")

    def getrpcinfo(self): return self.__call("getrpcinfo")

    def help(self, command: str=None): return self.__call("help", command)

    def logging(self, include_category_list: (list, tuple) = None, exclude_category_list: (list, tuple) = None):
        return self.__call("logging", include_category_list, exclude_category_list)

    def stop(self): return self.__call("stop")

    def uptime(self): return self.__call("uptime")

    # == Generating ==

    def generate(self, nblocks: int, maxtries: int = None): return self.__call("generate", nblocks, maxtries)

    def generatetoaddress(self, nblocks: int, address: str, maxtries: int = None):
        return self.__call("generatetoaddress", nblocks, address, maxtries)

    # == Mining ==

    def getblocktemplate(self, template_request: dict): return self.__call("getblocktemplate", template_request)

    def getmininginfo(self): return self.__call("getmininginfo")

    def getnetworkhashps(self, nblocks: int = None, height: int = None): return self.__call("getnetworkhashps", nblocks, height)

    def getstakinginfo(self): return self.__call("getstakinginfo")

    def submitblock(self, hexdata: str, dummy: str = None): return self.__call("submitblock", hexdata, dummy)

    def submitheader(self, hexdata: str): return self.__call("submitheader", hexdata)

    # == Network ==

    def addnode(self, node: str, command: str): return self.__call("addnode", node, command)

    def clearbanned(self): return self.__call("clearbanned")

    def disconnectnode(self, address: str = None, nodeid: int = None):
        if nodeid is not None and address is None:
            address = ""
        return self.__call("disconnectnode", address, nodeid)

    def getaddednodeinfo(self, node: str = None): return self.__call("getaddednodeinfo", node)

    def getconnectioncount(self): return self.__call("getconnectioncount")

    def getnettotals(self): return self.__call("getnettotals")

    def getnetworkinfo(self): return self.__call("getnetworkinfo")

    def getnodeaddresses(self, count: int = None): return self.__call("getnodeaddresses", count)

    def getpeerinfo(self): return self.__call("getpeerinfo")

    def listbanned(self): return self.__call("listbanned")

    def ping(self): return self.__call("ping")

    def setban(self, subnet: str, command: str, bantime: int = None, absolute: bool = None):
        return self.__call("setban", subnet, command, bantime, absolute)

    def setnetworkactive(self, state: str): return self.__call("setnetworkactive", state)

    # == Rawtransactions ==

    def decoderawtransaction(self, hexstring: str, iswitness: bool = None):
        return self.__call("decoderawtransaction", hexstring, iswitness)

    def fromhexaddress(self, hexaddress: str): return self.__call("fromhexaddress", hexaddress)

    def gethexaddress(self, address: str): return self.__call("gethexaddress", address)

    def getrawtransaction(self, txid: str, verbose: bool = None, blockhash: str = None):
        return self.__call("getrawtransaction", txid, verbose, blockhash)

    # == Util ==

    def createmultisig(self, nrequired: int, key_list: (list, tuple), address_type: str = None):
        return self.__call("createmultisig", nrequired, key_list, address_type)

    def deriveaddresses(self, descriptor: str, range_: (int, list, tuple) = None):
        return self.__call("deriveaddresses", descriptor, range_)

    def estimatesmartfee(self, conf_target: int, estimate_mode: str = None):
        return self.__call("estimatesmartfee", conf_target, estimate_mode)

    def getdescriptorinfo(self, descriptor: str): return self.__call("getdescriptorinfo", descriptor)

    def signmessagewithprivatekey(self, privkey: str, message: str):
        return self.__call("signmessagewithprivatekey", privkey, message)

    def validateaddress(self, address: str): return self.__call("validateaddress", address)

    def verifymessage(self, address: str, signature: str, message: str):
        return self.__call("verifymessage", address, signature, message)

    # == Wallet ==

    # TODO: Typed params from here down

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

    def sendtoaddress(self, address: str, amount: (int, float, str), comment: str = None, comment_to: str = None,
                      subtractfeefromamount: bool = None, replaceable: bool = None, conf_target: (int, str) = None,
                      estimate_mode: str = None, senderaddress: str = None, change_to_sender: bool = None):
        return self.__call("sendtoaddress", address, amount, comment, comment_to, subtractfeefromamount, replaceable,
                           conf_target, estimate_mode, senderaddress, change_to_sender)

    def sendtocontract(self, contractaddress, datahex, amount: (int, float, str) = None, gas_limit: int = None,
                       senderaddress: str = None, broadcast: bool = None, change_to_sender: bool = None):
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
