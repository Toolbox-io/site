import {Utils} from "./common.js";
import setUpTabs = Utils.setUpTabs;
import delay = Utils.delay;
import id = Utils.id;

(async () => {
    setUpTabs();

    await delay(1000);
    id("download").click();
})();