netsh interface ipv4 set dnsservers "Wi-Fi" static "1.1.1.1" primary
netsh interface ipv4 add dnsservers "Wi-Fi" "1.0.0.1" index=2
netsh interface ipv6 set dnsservers "Wi-Fi" static "2606:4700:4700::1111" primary
netsh interface ipv6 add dnsservers "Wi-Fi" "2606:4700:4700::1001" index=2

netsh interface ipv4 set dnsservers "Wi-Fi 2" static "1.1.1.1" primary
netsh interface ipv4 add dnsservers "Wi-Fi 2" "1.0.0.1" index=2
netsh interface ipv6 set dnsservers "Wi-Fi 2" static "2606:4700:4700::1111" primary
netsh interface ipv6 add dnsservers "Wi-Fi 2" "2606:4700:4700::1001" index=2

netsh interface ipv4 set dnsservers "Ethernet" static "1.1.1.1" primary
netsh interface ipv4 add dnsservers "Ethernet" "1.0.0.1" index=2
netsh interface ipv6 set dnsservers "Ethernet" static "2606:4700:4700::1111" primary
netsh interface ipv6 add dnsservers "Ethernet" "2606:4700:4700::1001" index=2
