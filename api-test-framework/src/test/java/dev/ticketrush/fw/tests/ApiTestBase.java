package dev.ticketrush.fw.tests;

import dev.ticketrush.fw.client.ApiClient;
import dev.ticketrush.fw.config.EnvConfig;
import dev.ticketrush.fw.data.SeatAllocator;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.BeforeSuite;

import static org.hamcrest.Matchers.equalTo;

public abstract class ApiTestBase {

    protected static final EnvConfig cfg = EnvConfig.get();
    protected final ApiClient api = new ApiClient(cfg);

    @BeforeSuite(alwaysRun = true)
    public void echoConfigAndCheckServer() {
        System.out.println("[config] " + cfg);
        api.health().then().statusCode(200).body("admin_enabled", equalTo(true));
    }

    @BeforeMethod(alwaysRun = true)
    public void freshData() {
        api.reset(0).then().statusCode(200);
        SeatAllocator.rewind();
    }
}
