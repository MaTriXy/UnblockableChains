from web3.utils.events import get_event_data
from web3.utils.abi import filter_by_name,abi_to_signature
from web3.utils.filters import  LogFilter
from .WalletOperations import encode_hex
from .LogWrapper import LogWrapper
from .PollerQueue import PollerQueue
import time

l = LogWrapper.getLogger()

def createLogEventFilter(eventName, contractAbi, fromAddress, web3, topicFilters:[]) -> (LogFilter, str):
	eventABI = filter_by_name(eventName, contractAbi)[0]
	eventSignature = abi_to_signature(eventABI)
	eventHash = web3.sha3(encode_hex(eventSignature))
	l.debug('creating log filter. eventSignature:', eventSignature, 'eventHash:', eventHash, 'filters:',topicFilters)

	commandFilter = web3.eth.filter({'from': fromAddress,
											   'topics': [eventHash]+topicFilters})
	return commandFilter, eventABI


def getLogEventArg(tx, eventABI, argName)\
		:
	data = get_event_data(eventABI, tx)
	return data['args'][argName]

def getField(tx,field):
	return tx[field]


def logTransactionCost(web3, txhash, transName, dataLength, logger) -> bool:
	receipt = web3.eth.getTransactionReceipt(txhash)
	if receipt:
		trans = web3.eth.getTransaction(txhash)
		to = receipt['to'] if receipt['to'] else receipt['contractAddress']
		# txHash, block Number, from, to, transaction name, gas Limit, gas Used, gas Price, total cost, data size
		logger.info(txhash, receipt['blockNumber'], receipt['from'], to, transName, trans['gas'], receipt['gasUsed'],
		       trans['gasPrice'], web3.fromWei(receipt['gasUsed'] * trans['gasPrice'], 'ether'),dataLength, sep='\t')
		return True
	return False

transactionCostLogger = PollerQueue(logTransactionCost)
transactionCostLogger.start()


def waitForNodeToSync(web3):
	l.info('waiting for node to sync...')
	while web3.eth.syncing or web3.eth.blockNumber == 0:
		l.debug('current synced block is:',
		        web3.eth.blockNumber if web3.eth.blockNumber == 0 else web3.eth.syncing['currentBlock'])
		time.sleep(1)
	l.info('chain Sync done!')