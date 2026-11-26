# Kpopium Routing

Публичные профили маршрутизации для Happ и INCY. Основа логики — RoscomVPN Whitelist и Default; геобазы предоставляются сторонним проектом RoscomVPN.

| Клиент | Whitelist | Default |
| --- | --- | --- |
| Happ | [JSON](https://raw.githubusercontent.com/qlinkil/kpopium-routing/main/HAPP/WHITELIST.json) | [JSON](https://raw.githubusercontent.com/qlinkil/kpopium-routing/main/HAPP/DEFAULT.json) |
| INCY | [JSON](https://raw.githubusercontent.com/qlinkil/kpopium-routing/main/INCY/WHITELIST.json) | [JSON](https://raw.githubusercontent.com/qlinkil/kpopium-routing/main/INCY/DEFAULT.json) |

## Режимы

- Whitelist: локальная сеть и белый список напрямую, остальное через прокси при отсутствии иных совпадений.
- Default: расширенный прямой доступ к российским и выбранным игровым сервисам.
- Оба: BLOCK → PROXY → DIRECT; явные прокси-правила для основных доменов AI-сервисов. Это не гарантия отсутствия утечек или доступности аккаунтов.
- DNS: Google DoH для удаленного резолвера, Яндекс DoH для локального.

## Обновления

В Happ версии геобаз закреплены в URL, в INCY используются незакрепленные URL. Содержимое геобаз INCY может меняться независимо от этого репозитория. Собственные .dat не собираются.

Перед обновлением: отдельная ветка, проверка JSON, проверка доступности геофайлов и тесты обоих клиентов. После успешных тестов — перенос в main и обновление LastUpdated. При проблемах — возврат проверенного содержимого с новым LastUpdated. Автоматическое обновление версий Happ пока не реализовано.

## Источники

- [RoscomVPN Routing](https://github.com/hydraponique/roscomvpn-routing)
- [GeoIP](https://github.com/hydraponique/roscomvpn-geoip)
- [GeoSite](https://github.com/hydraponique/roscomvpn-geosite)

Не публикуйте в этом репозитории индивидуальные ссылки подписок, ключи, токены и резервные копии. Профили не являются официальными профилями Happ, INCY или RoscomVPN.
