from . import following, discover, links, mutualaid, secret, unitedkingdom

algos = {
    following.uri: following.handler,
    discover.uri: discover.handler,
    links.uri: links.handler,
    secret.uri: secret.handler,
    mutualaid.uri: mutualaid.handler,
    unitedkingdom.uri: unitedkingdom.handler,
}
