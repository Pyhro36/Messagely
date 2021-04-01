# Protocole de transmission de messages textuels unicode simples (STUMTP)

Il s'agit d'une surcouche du protocole TCP
adaptée au module socket de Python qui
a pour but de permettre la transmission
de messages textuels unicode entre un
serveur et des clients

## Traitement en flux

Comme les messages sont envoyés decoupés
en paquets, il faut déterminer quel est le
nombre de paquets à recevoir exactement
pour recevoir le message en entier et
seulement le message.

C'est pourquoi dans l'envoi, les messages
sont immédiatement suivis du caractère
"FIN DE TEXTE", EOT, caractère 3 de la
table ASCII ("\3" en Python), pour marquer la fin du
message. Ceci permet d'être sûr que le
message a été reçu en entier et qu'il n'y
a pas à attendre d'autres paquets

## Fiabilité

Si la connexion est rompue, TCP accepte quand
meme potentiellement un dernier message a
envoyer. Ce message ne sera donc pas envoyé en
definitive et son envoi devra etre demande a
nouveau. Pour pouvoir assurer que tous les messages sont bien envoyés, ces derniers sont mis dans une file d'attente et sont renvoyés tant que l'expéditeur n'a pas reçu en retour un acquitement du message permettant d'identifier le message acquité. Les messages doivent donc avoir un ID qui est renvoyé en acquitement lorsque le message a bien été reçu.

Il faut donc envoyer avec les messages l'acquitement du dernier message reçu si des messages ont été reçus depuis le précédent envoi.
S'il n'y a pas de message à envoyer, le destinataire peut tout de même renvoyer l'acquitement seul dès qu'il possède la fenêtre d'envoi.

## Envoi des messages

Pour envoyer les messages, il faut
envoyer la concatenation du message même
avec le caractère EOT

## Réception des messages

Pour recevoir le message, il faut
revecoir des paquets et les décoder tant
que le dernier paquets reçu ne se termine
pas par le caractère EOT.

Il faut ensuite concaténer tous les
paquets reçus puis supprimer le dernier
caractère, qui est le caractère EOT.

Le message complet peut ensuite être
transmis aux couches supérieures de
l'application

