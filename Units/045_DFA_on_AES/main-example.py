from DFA_Attack import *

cipher_text = b'539ba31a988912a8bd8cec9331477402'

faulted_texts = [
	b'349ba31a9889126cbd8c6c9331017402',
	b'299ba31a988912a3bd8cca9331d67402',
	b'53d9a31a4c8912a8bd8cec8431479202',
	b'533da31ab48912a8bd8cec8731470502',
	b'539b3d1a987412a8a18cec93314774e1',
	b'539b741a981e12a8ab8cec93314774ff',
	b'539ba34b988902a8bdc7ec93ec477402',
	b'539ba3ac98899ea8bd49ec93f2477402'
]


key = DFA_attack(
		cipher=cipher_text,
		faults=faulted_texts,
		rounds=11
	).Crack_key()

print(key)

# https://blog.quarkslab.com/differential-fault-analysis-on-white-box-aes-implementations.html