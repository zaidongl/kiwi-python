@fix
Feature: FIX message construction and validation
  As a QA engineer
  I want to be able to construct and validate FIX messages from scenarios
  So that I can exercise FIX message generation and checksum/length validation

  Scenario Outline: Build and validate a FIX NewOrderSingle message
	Given a FixAgent is created with sender "<sender>" and target "<target>" and version "<version>"
	When I build a FIX message of type "<msg_type>" with MsgSeqNum <seq_num> and fields:
	  | tag | value |
	  | 55  | <symbol> |
	  | 54  | <side>   |
	  | 38  | <quantity> |
	Then the constructed FIX message should validate successfully
	And the BodyLength and CheckSum fields should be correct

	Examples:
	  | sender | target | version   | msg_type | seq_num | symbol | side | quantity |
	  | SENDER | TARGET | FIX.4.4    | D        | 1       | AAPL   | 1    | 100      |
	  | TRDR1  | EXCH1  | FIX.4.2    | D        | 7       | MSFT   | 2    | 250      |

