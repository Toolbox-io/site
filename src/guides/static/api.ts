export type GuideHeader = {
    "DisplayName": string,
    "Icon": string
}

export type GuideEntry = {
    name: string,
    header: GuideHeader
}

export type GuideJSON = GuideEntry[];