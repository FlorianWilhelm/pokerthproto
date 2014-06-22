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
* PlayerInfoRequestMessage
* PlayerInfoReplyMessage
* JoinExistingGameMessage
* JoinNewGameMessage
* JoinGameAckMessage
* GamePlayerJoinedMessage
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
* GameListPlayerLeftMessage (SOON)
* GameListAdminChangedMessage
* SubscriptionRequestMessage
* RejoinExistingGameMessage
* JoinGameFailedMessage
* GamePlayerLeftMessage (SOON)
* GameAdminChangedMessage
* RemovedFromGameMessage
* KickPlayerRequestMessage
* LeaveGameRequestMessage
* InvitePlayerToGameMessage
* InviteNotifyMessage
* RejectGameInvitationMessage
* RejectInvNotifyMessage
* GameStartRejoinMessage
* AllInShowCardsMessage (SOON)
* EndOfHandShowCardsMessage (SOON)
* EndOfHandHideCardsMessage (SOON)
* ShowMyCardsRequestMessage (SOON)
* AfterHandShowCardsMessage (SOON)
* EndOfGameMessage (SOON)
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
