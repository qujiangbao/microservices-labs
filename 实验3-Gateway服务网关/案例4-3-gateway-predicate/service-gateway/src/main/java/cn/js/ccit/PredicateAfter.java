package cn.js.ccit;

import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

/**
 * 生成 After 断言用的时间。打印“当前时间加 1 小时”，
 * 用这个未来时间做 After 时，当前请求匹配失败。
 */
public class PredicateAfter {
    public static void main(String[] args) {
        System.out.println(ZonedDateTime.now().plusHours(1)
                .format(DateTimeFormatter.ISO_ZONED_DATE_TIME));
    }
}
