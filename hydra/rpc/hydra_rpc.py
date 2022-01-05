import os
import argparse
import json
from urllib.parse import urlsplit, urlunsplit

from hydra.rpc.base import BaseRPC


class HydraRPC(BaseRPC):
    __url: str = f"main://127.0.0.1"
    __session = None
    __json = False

    MAINNET_PORT = 3389
    TESTNET_PORT = 13389

    def __init__(self, url: (str, tuple) = __url, wallet: str = None):
        self.__mainnet, self.__url = HydraRPC.__parse_url__(url, wallet) if not isinstance(url, tuple) else url
        super().__init__(self.__url)

    @property
    def url(self):
        return self.__url

    @staticmethod
    def __parse_url__(url: str, wallet: str = None):
        url_split = urlsplit(url)

        schemes_hydra = ("mainnet", "main", "testnet", "test")
        schemes_main = ("http", "mainnet", "main")
        schemes = schemes_main + ("testnet", "test")

        if url_split.scheme not in schemes:
            raise ValueError(f"Invalid scheme for url: {url}")

        path = url_split.path

        if wallet is not None:
            path = os.path.join(path, f"/wallet/{wallet}")

        netloc = str(url_split.netloc)

        if not url_split.username and not url_split.password:
            cookie_path = os.path.join(os.environ.get("HOME"), ".hydra/.cookie")

            if os.path.isfile(cookie_path):
                userpass = open(cookie_path).read().strip()
                netloc = f"{userpass}@{netloc}"

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
            path,
            url_split.query,
            url_split.fragment
        ))

    @staticmethod
    def __parse_param__(param: str):
        param = param.strip()

        if not len(param):
            return param

        if (param.startswith("'") and param.endswith("'")) or (param.startswith('"') and param.endswith('"')):
            return param[1:-1]

        try:
            return json.loads(param)
        except json.decoder.JSONDecodeError:
            try:
                return json.loads(f'"{param}"')
            except json.decoder.JSONDecodeError:
                raise

    @staticmethod
    def __parser__(parser: argparse.ArgumentParser):

        parser.add_argument("-r", "--rpc", default=os.environ.get("HY_RPC", HydraRPC.__url), type=str,
                            help="rpc url (env: HY_RPC)", required=False)

        parser.add_argument("-w", "--wallet", default=os.environ.get("HY_RPC_WALLET", None),
                            type=HydraRPC.__parse_param__,
                            help="wallet name (env: HY_RPC_WALLET)", required=False)

    @staticmethod
    def __from_parsed__(args: argparse.Namespace):
        return HydraRPC(url=HydraRPC.__parse_url__(args.rpc, args.wallet))

    @property
    def mainnet(self):
        return self.__mainnet

    def call(self, name: str, *args, raw=False):
        result = super().call(name, *filter(lambda a: a is not None, args))
        return result if raw else result.Value

    # == Blockchain ==

    def callcontract(self, address: str, data: str, sender_address: str = None, gas_limit: int = None):
        if gas_limit is not None and sender_address is None:
            sender_address = ""

        return self.call("callcontract", address, data, sender_address, gas_limit)

    def getaccountinfo(self, address: str): return self.call("getaccountinfo", address)

    def getbestblockhash(self): return self.call("getbestblockhash")

    def getblock(self, blockhash: str, verbosity: int = None):
        return self.call("getblock", blockhash, verbosity)

    def getblockchaininfo(self): return self.call("getblockchaininfo")

    def getblockcount(self): return self.call("getblockcount")

    def getblockhash(self, height: int): return self.call("getblockhash", height)

    def getblockheader(self, blockhash: str, verbose: bool = None):
        return self.call("getblockheader", blockhash, verbose)

    def getblockstats(self, hash_or_height: (int, str), stats: (list, tuple) = None):
        return self.call("getblockstats", hash_or_height, stats)

    def getchaintips(self): return self.call("getchaintips")

    def getchaintxstats(self, nblocks: int = None, blockhash: str = None):
        return self.call("getchaintxstats", nblocks, blockhash)

    def getcontractcode(self, address: str): return self.call("getcontractcode", address)

    def getdifficulty(self): return self.call("getdifficulty")

    def getestimatedannualroi(self): return self.call("getestimatedannualroi")

    def getmempoolancestors(self, txid: str, verbose: bool = None): return self.call("getmempoolancestors", txid, verbose)

    def getmempooldescendants(self, txid: str, verbose: bool = None): return self.call("getmempooldescendants", txid, verbose)

    def getmempoolentry(self, txid: str): return self.call("getmempoolentry", txid)

    def getmempoolinfo(self): return self.call("getmempoolinfo")

    def getrawmempool(self, verbose: bool = None): return self.call("getrawmempool", verbose)

    def getstorage(self, address: str, block_num: int = None, index: int = None):
        return self.call("getstorage", address, block_num, index)

    def gettransactionreceipt(self, hash_: str): return self.call("gettransactionreceipt", hash_)

    def gettxout(self, txid: str, n: int, include_mempool: bool = None):
        return self.call("gettxout", txid, n, include_mempool)

    def gettxoutproof(self, txid_list: (list, tuple), blockhash: str = None):
        if isinstance(txid_list, str):
            txid_list = (txid_list,)

        return self.call("gettxoutproof", txid_list, blockhash)

    def gettxoutsetinfo(self): return self.call("gettxoutsetinfo")

    def listcontracts(self, start: int = None, max_display: int = None):
        return self.call("listcontracts", start, max_display)

    def preciousblock(self, blockhash: str): return self.call("preciousblock", blockhash)

    def pruneblockchain(self, height: int): return self.call("pruneblockchain", height)

    def savemempool(self, height: int): return self.call("savemempool", height)

    def scantxoutset(self, action: str, scanobjects_list: (list, tuple)):
        if isinstance(scanobjects_list, str):
            scanobjects_list = (scanobjects_list,)
        return self.call("scantxoutset", action, scanobjects_list)

    def searchlogs(self, from_block: int, to_block: int, address: str = None, topics: (list, tuple) = None,
                   minconf: int = None):
        return self.call("searchlogs", from_block, to_block, address, topics, minconf)

    def verifychain(self, checklevel: int = None, nblocks: int = None): return self.call("verifychain", checklevel, nblocks)

    def verifytxoutproof(self, proof: str): return self.call("verifytxoutproof", proof)

    def waitforlogs(self, from_block: int = None, to_block: int = None, filter_: str = None, minconf: int = None):
        return self.call("waitforlogs", from_block, to_block, filter_, minconf)

    # == Control ==

    def getdgpinfo(self): return self.call("getdgpinfo")

    def getinfo(self): return self.call("getinfo")

    def getmemoryinfo(self, mode: str = None): return self.call("getmemoryinfo", mode)

    def getoracleinfo(self): return self.call("getoracleinfo")

    def getrpcinfo(self): return self.call("getrpcinfo")

    def help(self, command: str=None): return self.call("help", command)

    def logging(self, include_category_list: (list, tuple) = None, exclude_category_list: (list, tuple) = None):
        return self.call("logging", include_category_list, exclude_category_list)

    def stop(self): return self.call("stop")

    def uptime(self): return self.call("uptime")

    # == Generating ==

    def generate(self, nblocks: int, maxtries: int = None): return self.call("generate", nblocks, maxtries)

    def generatetoaddress(self, nblocks: int, address: str, maxtries: int = None):
        return self.call("generatetoaddress", nblocks, address, maxtries)

    # == Mining ==

    def getblocktemplate(self, template_request: dict): return self.call("getblocktemplate", template_request)

    def getmininginfo(self): return self.call("getmininginfo")

    def getnetworkhashps(self, nblocks: int = None, height: int = None): return self.call("getnetworkhashps", nblocks, height)

    def getstakinginfo(self): return self.call("getstakinginfo")

    def submitblock(self, hexdata: str, dummy: str = None): return self.call("submitblock", hexdata, dummy)

    def submitheader(self, hexdata: str): return self.call("submitheader", hexdata)

    # == Network ==

    def addnode(self, node: str, command: str): return self.call("addnode", node, command)

    def clearbanned(self): return self.call("clearbanned")

    def disconnectnode(self, address: str = None, nodeid: int = None):
        if nodeid is not None and address is None:
            address = ""
        return self.call("disconnectnode", address, nodeid)

    def getaddednodeinfo(self, node: str = None): return self.call("getaddednodeinfo", node)

    def getconnectioncount(self): return self.call("getconnectioncount")

    def getnettotals(self): return self.call("getnettotals")

    def getnetworkinfo(self): return self.call("getnetworkinfo")

    def getnodeaddresses(self, count: int = None): return self.call("getnodeaddresses", count)

    def getpeerinfo(self): return self.call("getpeerinfo")

    def listbanned(self): return self.call("listbanned")

    def ping(self): return self.call("ping")

    def setban(self, subnet: str, command: str, bantime: int = None, absolute: bool = None):
        return self.call("setban", subnet, command, bantime, absolute)

    def setnetworkactive(self, state: str): return self.call("setnetworkactive", state)

    # == Rawtransactions ==

    def decoderawtransaction(self, hexstring: str, iswitness: bool = None):
        return self.call("decoderawtransaction", hexstring, iswitness)

    def fromhexaddress(self, hexaddress: str): return self.call("fromhexaddress", hexaddress)

    def gethexaddress(self, address: str): return self.call("gethexaddress", address)

    def getrawtransaction(self, txid: str, verbose: bool = None, blockhash: str = None):
        return self.call("getrawtransaction", txid, verbose, blockhash)

    # == Util ==

    def createmultisig(self, nrequired: int, key_list: (list, tuple), address_type: str = None):
        return self.call("createmultisig", nrequired, key_list, address_type)

    def deriveaddresses(self, descriptor: str, range_: (int, list, tuple) = None):
        return self.call("deriveaddresses", descriptor, range_)

    def estimatesmartfee(self, conf_target: int, estimate_mode: str = None):
        return self.call("estimatesmartfee", conf_target, estimate_mode)

    def getdescriptorinfo(self, descriptor: str): return self.call("getdescriptorinfo", descriptor)

    def signmessagewithprivatekey(self, privkey: str, message: str):
        return self.call("signmessagewithprivatekey", privkey, message)

    def validateaddress(self, address: str): return self.call("validateaddress", address)

    def verifymessage(self, address: str, signature: str, message: str):
        return self.call("verifymessage", address, signature, message)

    # == Wallet ==

    # TODO: Typed params from here down

    def addmultisigaddress(self, nrequired, key_list, label=None, address_type=None):
        if address_type is not None and label is None:
            label = ''
        return self.call("addmultisigaddress", nrequired, key_list, label, address_type)

    def backupwallet(self, destination): return self.call("backupwallet", destination)

    def craetecontract(self, bytecode, gas_limit, senderaddress=None, broadcast=None, change_to_sender=None):
        return self.call("craetecontract", bytecode, gas_limit, senderaddress, broadcast, change_to_sender)

    def createwallet(self, wallet_name, disable_private_keys=None, blank=None):
        return self.call("createwallet", wallet_name, disable_private_keys, blank)

    def dumpprivkey(self, address): return self.call("dumpprivkey", address)

    def dumpwallet(self, filename): return self.call("dumpwallet", filename)

    def encryptwallet(self, passphrase): return self.call("encryptwallet", passphrase)

    def getaddressesbylabel(self, label=""): return self.call("getaddressesbylabel", label)

    def getaddressinfo(self, address): return self.call("getaddressinfo", address)

    def getbalance(self, dummy=None, minconf=None, include_watchonly=None):
        return self.call("getbalance", dummy, minconf, include_watchonly)

    def getbalanceofaddress(self, address): return self.call("getbalanceofaddress", address)

    def getnewaddress(self, label="", address_type=None): return self.call("getnewaddress", label, address_type)

    def getrawchangeaddress(self, address_type=None): return self.call("getrawchangeaddress", address_type)

    def getreceivedbyaddress(self, address, minconf=None): return self.call("getreceivedbyaddress", address, minconf)

    def getreceivedbylabel(self, label="", minconf=None): return self.call("getreceivedbylabel", label, minconf)

    def gettransaction(self, txid, include_watchonly=None, waitconf=None):
        return self.call("gettransaction", txid, include_watchonly, waitconf)

    def getunconfirmedbalance(self): return self.call("getunconfirmedbalance")

    def getwalletinfo(self): return self.call("getwalletinfo")

    def importaddress(self, address, label=None, rescan=None, p2sh=None):
        if rescan is not None and label is None:
            label = ""
        return self.call("importaddress", address, label, rescan, p2sh)

    def importmulti(self, requests_, options=None): return self.call("importmulti", requests_, options)

    def importprivkey(self, hydraprivkey, label="", rescan=None):
        return self.call("importprivkey", hydraprivkey, label, rescan)

    def importprunedfunds(self, rawtransaction, txoutproof):
        return self.call("importprunedfunds", rawtransaction, txoutproof)

    def importpubkey(self, pubkey, label="", rescan=None): return self.call("importpubkey", pubkey, label, rescan)

    def importwallet(self, filename): return self.call("importwallet", filename)

    def keypoolrefill(self, newsize=None): return self.call("keypoolrefill", newsize)

    def listaddressgroupings(self): return self.call("listaddressgroupings")

    def listlabels(self, purpose=None): return self.call("listlabels", purpose)

    def listlockunspent(self): return self.call("listlockunspent")

    def listreceivedbyaddress(self, minconf=None, include_empty=None, include_watchonly=None, address_filter=None):
        return self.call("listreceivedbyaddress", minconf, include_empty, include_watchonly, address_filter)

    def listreceivedbylabel(self, minconf=None, include_empty=None, include_watchonly=None):
        return self.call("listreceivedbylabel", minconf, include_empty, include_watchonly)

    def listsinceblock(self, blockhash, target_confirmations=None, include_watchonly=None, include_removed=None):
        return self.call("listsinceblock", blockhash, target_confirmations, include_watchonly, include_removed)

    def listtransactions(self, label="", count=None, skip=None, include_watchonly=None):
        return self.call("listtransactions", label, count, skip, include_watchonly)

    def listunspent(self, minconf=None, maxconf=None, address_list=None, include_unsafe=None, query_options=None):
        return self.call("listunspent", minconf, maxconf, address_list, include_unsafe, query_options)

    def listwalletdir(self): return self.call("listwalletdir")

    def listwallets(self): return self.call("listwallets")

    def loadwallet(self, filename): return self.call("loadwallet", filename)

    def lockunspent(self, unlock, txid_vout_list=None): return self.call("lockunspent", unlock, txid_vout_list)

    def removeprunedfunds(self, txid): return self.call("removeprunedfunds", txid)

    def rescanblockchain(self, start_height=None, stop_height=None):
        return self.call("rescanblockchain", start_height, stop_height)

    def reservebalance(self, reserve=None, amount=None): return self.call("reservebalance", reserve, amount)

    def sendtoaddress(self, address: str, amount: (int, float, str), comment: str = None, comment_to: str = None,
                      subtractfeefromamount: bool = None, replaceable: bool = None, conf_target: (int, str) = None,
                      estimate_mode: str = None, senderaddress: str = None, change_to_sender: bool = None):
        return self.call("sendtoaddress", address, amount, comment, comment_to, subtractfeefromamount, replaceable,
                           conf_target, estimate_mode, senderaddress, change_to_sender)

    def sendtocontract(self, contractaddress, datahex, amount: (int, float, str) = None, gas_limit: int = None,
                       senderaddress: str = None, broadcast: bool = None, change_to_sender: bool = None):
        return self.call("sendtocontract", contractaddress, datahex, amount, gas_limit, senderaddress, broadcast,
                           change_to_sender)

    def sethdseed(self, newkeypool=None, seed=None): return self.call("sethdseed", newkeypool, seed)

    def setlabel(self, address, label): return self.call("setlabel", address, label)

    def settxfee(self, amount): return self.call("settxfee", amount)

    def signmessage(self, address, message): return self.call("signmessage", address, message)

    def signrawsendertransactionwithwallet(self, hexstring, sighashtype=None):
        return self.call("signrawsendertransactionwithwallet", hexstring, sighashtype)

    def signrawtransactionwithwallet(self, hexstring, txid_entry_list, sighashtype=None):
        return self.call("signrawtransactionwithwallet", hexstring, txid_entry_list, sighashtype)

    def unloadwallet(self, wallet_name=None): return self.call("unloadwallet", wallet_name)

    def walletlock(self): return self.call("walletlock")

    def walletpassphrase(self, passphrase, timeout, staking_only=None):
        return self.call("walletpassphrase", passphrase, timeout, staking_only)

    def walletpassphrasechange(self, oldpassphrase, newpassphrase):
        return self.call("walletpassphrasechange", oldpassphrase, newpassphrase)
