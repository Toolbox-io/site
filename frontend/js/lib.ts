// @ts-ignore
import { marked as marked1 } from "/node_modules/marked/lib/marked.esm.js";
// @ts-ignore
import hljs1 from "/node_modules/@highlightjs/cdn-assets/es/core.js";
// @ts-ignore
import xml1 from "/node_modules/@highlightjs/cdn-assets/es/languages/xml.min.js";

// ------
// Marked
// ------
export interface MarkedOptions {
    gfm?: boolean;
    breaks?: boolean;
    headerIds?: boolean;
    mangle?: boolean;
    sanitize?: boolean;
    silent?: boolean;
    smartLists?: boolean;
    smartypants?: boolean;
    xhtml?: boolean;
}

export interface MarkedExtension {
    name: string;
    level?: string;
    start?: (src: string) => number;
    tokenizer?: (src: string, tokens: any[]) => any;
    renderer?: (tokens: any[], idx: number, options: MarkedOptions) => string;
}

export interface Marked {
    parse(text: string, options?: MarkedOptions): string;
    parseInline(text: string, options?: MarkedOptions): string;
    setOptions(options: MarkedOptions): void;
    use(extension: MarkedExtension): void;
    walkTokens(tokens: any[], callback: (token: any) => void): void;
}

export let marked = marked1 as Marked


// ------------
// Highlight.js
// ------------
export interface HighlightOptions {
    language?: string;
    ignoreIllegals?: boolean;
}

export interface HighlightResult {
    relevance: number;
    value: string;
    language: string;
    top?: any;
}

export interface Language {
    name: string;
    aliases?: string[];
    keywords?: any;
    contains?: any[];
}

export interface HighlightJS {
    highlight(code: string, options: HighlightOptions): HighlightResult;
    highlightAuto(code: string, options?: HighlightOptions): HighlightResult;
    highlightAll(): void;
    highlightElement(element: HTMLElement): void;
    highlightBlock(element: HTMLElement): void;
    configure(options: any): void;
    registerLanguage(name: string, language: Language): void;
    listLanguages(): string[];
    getLanguage(name: string): Language | undefined;
    autoDetection(name: string): boolean;
    highlightAllUnder(element: HTMLElement): void;
    highlightElement(element: HTMLElement, options?: HighlightOptions): void;
}

export let hljs = hljs1 as HighlightJS
export let xml = xml1 as Language