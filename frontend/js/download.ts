import { delay, id, setUpTabs } from "./common/utils";

setUpTabs();

await delay(1000);
id("download")!.click();