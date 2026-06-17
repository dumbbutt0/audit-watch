## Inadequate distributed system design 

ZetaChain is a complex distributed system, involving many components running both physically distributed and in parallel: various source and destination blockchains, ZetaChain itself, observers, signers... This kind of distributed/concurrent system require a very rigorous approach to design and coding; the failure to cover all component interactions may lead to catastrophic consequences. 

At the same time, we, even in the limited allotted time, and with our attention focused mainly on the `x/observer` module and its dependencies, could not help but notice that ZetaChain is designed and programmed in a way that is more suitable for a sequential system than a complex distributed system. Particular symptoms we would like to point out include:

- Fixed number of retries for remote calls, such as in [zetaclient/tx.go::PostSend()](https://github.com/code-423n4/2023-11-zetachain/blob/0df9a114103b6ed7536d65a03e2e4876eb8bdbc0/repos/node/zetaclient/tx.go#L133-L141) or [zetaclient/btc_signer.go::TryProcessOutTx()](https://github.com/code-423n4/2023-11-zetachain/blob/0df9a114103b6ed7536d65a03e2e4876eb8bdbc0/repos/node/zetaclient/btc_signer.go#L351), and many other places
- Fixed, hard-coded timeouts, such as in [rpc/namespaces/ethereum/eth/filters/filter_system.go::consumeEvents()](https://github.com/code-423n4/2023-11-zetachain/blob/0df9a114103b6ed7536d65a03e2e4876eb8bdbc0/repos/node/rpc/namespaces/ethereum/eth/filters/filter_system.go#L287) or [zetaclient/tx.go::PostGasPrice()](https://github.com/code-423n4/2023-11-zetachain/blob/0df9a114103b6ed7536d65a03e2e4876eb8bdbc0/repos/node/zetaclient/tx.go#L98), and many other places.


While the above are rather superficial aspects, more serious issues manifest themselves in the overall system design, and in the assumptions being made throughout it. 

### Disregard of concurrent executions

ZetaChain, with all its components running in parallel, exhibits a plethora of concurrent executions. As we know from concurrency theory, concurrent bugs, and in particular race conditions, are notoriously hard to test for, and tend to manifest themselves unexpectedly, with catastrophic consequences. One finding of ours belong to that category, namely **Dynamics of chain observers may render ballots unfinalizable due to static voter lists**. In the bug exemplified by the finding, the implicit assumption of immutability of the chain observers is made, which is violated by (concurrent) events that happen between the start point (creation of a ballot), and the end point (authorization checks when adding votes to the ballot) of a particular concurrent execution (casting multiple votes on a single ballot). 

We recommend to carefully inspect the codebase for all data that is subject to the influence by concurrent executions, and to correct all present implicit assumptions on the behavior of such data, by either protecting it (locks/mutexes), or accounting for the possibilities of the data changes at the protocol level.


### Assumptions of a synchronous execution of distributed components

ZetaChain consists of multiple components which are physically independent entities (with independent control flow). As we know from the distributed systems theory, there are several well established paradigms for distributed communication, with Asynchronous Message Passing, and Remote Procedure Calls being the two most prominent ones. The problem is that ZetaChain doesn't implement any of those consistently, but combines various bits and pieces from all communication styles, resulting in a highly fragile system.

One finding of ours, **Failures of inbound transactions will lead to deposited funds loss and other failures**, demonstrates this particular problem. In the finding we demonstrate that the transactions are posted from ZetaClient to ZetaChain, and are regarded as if it's a synchronous procedure call, while in reality it's an asynchronous message passing. The result of this mismatch is that the submitted transaction may fail on ZetaChain at a later time point, when the component that submitted it (ZetaClient) has already progressed beyond any possibility to react to the failure.

Another issue we have noticed but have not reported as a standalone finding, is in [observeInTX()](https://github.com/code-423n4/2023-11-zetachain/blob/0df9a114103b6ed7536d65a03e2e4876eb8bdbc0/repos/node/zetaclient/evm_client.go#L784). Here the function is requesting the information *from ZetaChain*, `crosschainFlags, err := ob.zetaClient.GetCrosschainFlags()`, *in real time*, and then taking *actions wrt. Ethereum* based on the outcome of that call. This is yet another example of synchrony assumptions on remote calls, when one component, ZetaClient, tries to synchronize the state of three distributed components (ZetaClient itself, and two blockchains), in a single function: an attempt which is bound to fail, with serious consequences.

We recommend to carefully inspect all places where one component of ZetaChain invokes other components, or sends messages to them. We propose, for each communication, to classify whether an interaction belongs (or should belong) to a particular pattern of distributed communication. Should it be asynchronous message passing? Should it be a remote procedure call? Both variants are possible, but the system designers need to have clarity in that respect. After such classification is performed, an understanding needs to be achieved on how this communication integrates into the overall ZetaChain workflow, and whether the errors in a particular interaction can disrupt ZetaChain functionality (more on that below). Accordingly, for various parts of ZetaChain, some communication patterns might be more appropriate than others, and the currently employed solutions might need to change. While in some cases local code modifications may suffice, e.g. to strengthen the error handling, in others it might be necessary to redesign the core ZetaChain protocols (e.g. to switch from RPC to asynchronous message passing).


### Inconsistent handling of errors in distributed interactions

As we have pointed out above, in many cases ZetaChain designers don't seem to adhere to a particular distributed communication style. This manifests itself also in the inconsistent handling of errors wrt. distributed communication between ZetaChain components. Below we list a few examples:

- The [retry loop in zetaclient/btc_signer.go::TryProcessOutTx()](https://github.com/code-423n4/2023-11-zetachain/blob/0df9a114103b6ed7536d65a03e2e4876eb8bdbc0/repos/node/zetaclient/btc_signer.go#L350-L370) performs the fixed number of retries (5); if broadcasting of a transaction fails during one of the first 4 retries, the call is repeated, but after the 5th failed attempt, **the execution will proceed as if it was successful**.
- Function [observeInTX()](https://github.com/code-423n4/2023-11-zetachain/blob/0df9a114103b6ed7536d65a03e2e4876eb8bdbc0/repos/node/zetaclient/evm_client.go#L774-L993) scans EVM logs, performing multiple tasks (querying and processing zeta sent logs, deposited logs, incoming txs to TSS address). While doing so, the function performs multiple passes over EVM blocks, executing various operations. When errors occur in those operations, for some errors the code continues (thus ignoring the error, and skipping the current block/event), for others the function returns, thus terminating the processing. The consequences of such inconsistent error handling are unclear, and we have not been able to investigate further due to the limited time we could allocate for this audit; but we strongly suspect that many dangerous failures may result from that (e.g. ignoring a valid deposit may lead to the loss of funds, or always terminating processing on the same event over and over again may result in DOS).

Thus, the current approach to error handling in distributed computations in ZetaChain seems to be adhoc, not following clear patterns or rules. We recommend to clearly formulate the development guidelines and rules for various situations (e.g. how to handle errors in RPC; how to handle errors when submitting transactions; how to track when the transaction was successful; when processing of a particular event can be considered complete, or should be retried after some time, etc.) and strictly enforce these rules in every case of distributed communication.


### Mismatch between modes of operation and economic incentives for ZetaChain and ZetaClient

Validators running ZetaChain binaries, by doing so, participate in the Proof-of-Stake mechanism, which provides the necessary economic incentives for validators to act in a honest and timely manner. At the same time, the same validators running ZetaClients don't have any economic incentives: they are not bound by any rules; they are only _allowed_ to participate in the ZetaChain observation procedure, but _not required_ to. We see a high risk for ZetaChain is such absence of economic incentives for the validators to run ZetaClient, which may lead to:

- Denial of service, not due to malevolence, but negligence: validators, lacking incentives, won't be watching ZetaClients closely to ensure their timely and correct operation
- Disruption of ZetaChain operations due to malevolence from some validators, which might either individually or in groups vote on (false) observations that could benefit them financially. While there might be no particular reasons to suspect bad intentions from validators, as there is no punishment for misbehavior, this scenario can't be excluded from consideration.

We would like also to point out at a substantial difference in modes of operation between ZetaChain Proof-of-Stake voting mechanism, and ZetaClient observation voting procedure. 
  
- Proof-of-Stake mechanism gives validators the voting power proportional to their stake in the system
- Observation voting procedure gives all validators equal voting power irrespective of their stake in the Proof-of-Stake system.

This mismatch in mechanism design further worsens ZetaChain stability, by providing small validators disproportionally high power when voting on observations. While large validators have their reputation at stake, and heavily invest in the security of their infrastructure, for small ones neither reputation nor security are not prevailing concerns.

We recommend to mimic in the ZetaClient observation voting procedure the Proof-of-Stake mechanism of ZetaChain, and to track and punish misbehavior during observation voting in the same way as it's done for the Proof-of-Stake validation.

### Time spent:
40 hours