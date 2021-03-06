========================
Status of Implementation
========================

The PokerTH protocol consists of 81 different messages types which are all
enveloped inside an ``PokerTHMessage``. Only a subset of all messages is needed
in most cases.

Implemented
===========

* AnnounceMessage
* InitMessage
* InitAckMessage
* PlayerListMessage
* GameListNewMessage
* GameListUpdateMessage
* GameListPlayerJoinedMessage
* GameListPlayerLeftMessage
* PlayerInfoRequestMessage
* PlayerInfoReplyMessage
* JoinExistingGameMessage
* JoinNewGameMessage
* JoinGameAckMessage
* GamePlayerJoinedMessage
* GamePlayerLeftMessage
* StartEventMessage
* StartEventAckMessage
* GameStartInitialMessage
* HandStartMessage
* PlayersTurnMessage
* MyActionRequestMessage
* YourActionRejectedMessage
* PlayersActionDoneMessage
* DealFlopCardsMessage
* DealTurnCardMessage
* DealRiverCardMessage
* ChatMessage
* ChatRequestMessage
* AllInShowCardsMessage
* EndOfHandShowCardsMessage
* EndOfHandHideCardsMessage
* ShowMyCardsRequestMessage
* AfterHandShowCardsMessage
* EndOfGameMessage


Not Implemented
===============

* AuthServerChallengeMessage
* AuthClientResponseMessage
* AuthServerVerificationMessage
* AvatarRequestMessage
* AvatarHeaderMessage
* AvatarDataMessage
* AvatarEndMessage
* UnknownAvatarMessage
* GameListAdminChangedMessage
* SubscriptionRequestMessage
* RejoinExistingGameMessage
* JoinGameFailedMessage
* GameAdminChangedMessage
* RemovedFromGameMessage
* KickPlayerRequestMessage
* LeaveGameRequestMessage
* InvitePlayerToGameMessage
* InviteNotifyMessage
* RejectGameInvitationMessage
* RejectInvNotifyMessage
* GameStartRejoinMessage
* PlayerIdChangedMessage (SOON)
* AskKickPlayerMessage
* AskKickDeniedMessage
* StartKickPetitionMessage
* VoteKickRequestMessage
* VoteKickReplyMessage
* KickPetitionUpdateMessage
* EndKickPetitionMessage
* StatisticsMessage
* ChatRejectMessage
* DialogMessage
* TimeoutWarningMessage
* ResetTimeoutMessage
* ReportAvatarMessage
* ReportAvatarAckMessage
* ReportGameMessage
* ReportGameAckMessage
* ErrorMessage
* AdminRemoveGameMessage
* AdminRemoveGameAckMessage
* AdminBanPlayerMessage
* AdminBanPlayerAckMessage
* GameListSpectatorJoinedMessage
* GameListSpectatorLeftMessage
* GameSpectatorJoinedMessage
* GameSpectatorLeftMessage
