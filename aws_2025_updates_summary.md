
---

# AWS 在泰国曼谷宣布新的 AWS Direct Connect 位置和扩展

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/01/aws-direct-connect-location-expansion-bangkok-thailand/](https://aws.amazon.com/about-aws/whats-new/2025/01/aws-direct-connect-location-expansion-bangkok-thailand/)  

**发布时间:** 2025-01-08  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS 在泰国曼谷宣布新的 AWS Direct Connect 位置和扩展  

发布于：2025 年 1 月 8 日  

今天，AWS 宣布在泰国曼谷的 Telehouse 数据中心开设一个新的 AWS Direct Connect (AWS Direct Connect) 位置。通过将您的网络连接到 AWS 在新曼谷位置，您可以获得对所有公共 AWS 区域（除中国区域外）、AWS GovCloud 区域以及 AWS Local Zones (AWS Local Zones) 的私有直接访问。这个位置是泰国境内的第二个 AWS Direct Connect 位置。新 Direct Connect 位置提供专用的 10 Gbps 和 100 Gbps 连接，并支持 MACsec (MACsec) 加密。  
  
AWS 还宣布在现有的 TCC, 曼谷 Direct Connect 位置添加 10 Gbps 和 100 Gbps MACsec 服务。  
  
Direct Connect 服务 (Direct Connect service) 使您能够建立 AWS 与您的数据中心、办公室或联席托管环境之间的私有物理网络连接。这些私有连接可以提供比通过公共互联网连接更稳定的网络体验。  
  
有关全球超过 145 个 Direct Connect 位置的更多信息，请访问 Direct Connect [位置](https://aws.amazon.com/directconnect/locations/) 部分，或查看 [产品详情页面](https://aws.amazon.com/directconnect)。或者，访问我们的 [入门页面](https://aws.amazon.com/directconnect/getting-started/)，了解如何购买和部署 Direct Connect。

---

# Amazon MSK Connect APIs 现已支持 AWS PrivateLink

**原始链接:** [原始链接](https://aws.amazon.com/about-aws/whats-new/2025/01/amazon-msk-connect-apis-aws-privatelink)  

**发布时间:** 2025-01-08  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon MSK Connect APIs 现已支持 AWS PrivateLink  

发表于: 2025 年 1 月 8 日  

Amazon Managed Streaming for Apache Kafka Connect (Amazon MSK Connect) APIs 现已支持 [AWS PrivateLink](https://aws.amazon.com/privatelink/)，允许您从 Amazon Virtual Private Cloud (VPC) 内调用 Amazon MSK Connect APIs，而无需通过公共互联网。  

默认情况下，MSK 集群与 Amazon MSK Connect 连接器之间的所有通信均为私有的，且数据从不通过互联网传输。与 Amazon MSK APIs 的 AWS PrivateLink 支持类似，此次发布使客户端能够通过私有端点调用 MSK Connect APIs。这让具有严格安全要求的客户端应用程序能够执行 MSK Connect 特定操作，例如从新或现有自定义插件创建连接器、列出和描述连接器详情，或更新连接器，而无需使用公共连接。  

AWS PrivateLink 支持 Amazon MSK Connect 的功能已在所有提供 Amazon MSK Connect 的 AWS 区域可用。要开始使用，请参考 [AWS PrivateLink 文档](https://docs.aws.amazon.com/en_us/vpc/latest/privatelink/privatelink-access-aws-services.html) 中的指南。要了解更多关于 Amazon MSK Connect 的信息，请访问 Amazon MSK Connect [文档](https://docs.aws.amazon.com/msk/latest/developerguide/msk-connect.html)。

---

# AWS Security Hub 现已集成 Amazon Route 53 Resolver DNS Firewall

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/01/aws-security-hub-route-53-resolver-dns-firewall/](https://aws.amazon.com/about-aws/whats-new/2025/01/aws-security-hub-route-53-resolver-dns-firewall/)  

**发布时间:** 2025-01-13  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS Security Hub 现已集成 Amazon Route 53 Resolver DNS Firewall  

发表于: 2025 年 1 月 13 日  

[AWS Security Hub](https://aws.amazon.com/security-hub/) 现支持 Amazon Route 53 Resolver DNS Firewall (Amazon Route 53 Resolver DNS 防火墙)，让您能够针对从 Amazon VPC (Amazon Virtual Private Cloud) 中发出的 DNS 查询接收安全发现，这些查询涉及可疑的恶意域名 或 声誉低的域名。Route 53 Resolver DNS 防火墙是一种托管防火墙，可帮助您阻止针对恶意域名的 DNS 查询，同时允许针对可信域名的查询。  
  
如今，AWS Security Hub 为您提供对 AWS 账户的安全警报和合规状态的全面视图。这一集成让您能够启用三种新的 Security Hub 发现类型。您现在可以接收针对与 AWS 托管域名列表 (AWS Managed Domain Lists)、客户域名列表以及 Route 53 Resolver DNS 防火墙高级 (Route 53 Resolver DNS Firewall Advanced) 识别的威胁相关的被阻止或警报查询的安全发现。通过此发布，您可以在一个地方查看可能与恶意 DNS 查询相关的账户安全发现，同时与其他 AWS 服务（如 Amazon GuardDuty、Amazon Inspector 和 Amazon Macie）的发现放在一起。  
  
此功能在所有提供 Amazon Route 53 Resolver DNS 防火墙的 AWS 区域可用。请参阅 [此处](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall-availability.html) 以获取 Route 53 Resolver DNS 防火墙可用区域列表。要了解更多关于 AWS Security Hub 功能的信息，请参阅 AWS Security Hub [文档](https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html)。要了解更多关于 Route 53 Resolver DNS 防火墙的信息，请参阅 [产品页面](https://aws.amazon.com/route53/resolver-dns-firewall/) 或 [文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall.html)。

---

# AWS 宣布在墨西哥 Querétaro 新增 AWS Direct Connect 位置并扩展

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/01/aws-direct-connect-expansion-queretaro-mexico/](https://aws.amazon.com/about-aws/whats-new/2025/01/aws-direct-connect-expansion-queretaro-mexico/)  

**发布时间:** 2025-01-14  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS 宣布在墨西哥 Querétaro 新增 AWS Direct Connect 位置并扩展  

发表于: 2025 年 1 月 14 日  

今天，AWS 宣布在 Equinix MX1 数据中心（位于墨西哥城附近的 Querétaro，墨西哥）内开设一个新的 AWS Direct Connect 位置。通过将您的网络连接到 AWS 的新位置，您可以获得对所有公共 AWS 区域（除中国区域外）、AWS GovCloud 区域以及本地扩展区域 (AWS Local Zones) 的私有直接访问。这个站点是墨西哥的第二个 AWS Direct Connect 位置。新 Direct Connect 位置提供专用的 10 Gbps 和 100 Gbps 连接，并支持 MACsec 加密。  

AWS 还宣布在现有 KIO Networks 数据中心（位于墨西哥 Querétaro）中新增 10 Gbps 和 100 Gbps MACsec 服务。  

Direct Connect 服务让您能够在 AWS 和您的数据中心、办公室或共址环境之间建立私有物理网络连接。这些私有连接可以提供比通过公共互联网连接更稳定的网络体验。  

有关全球超过 145 个 Direct Connect 位置的更多信息，请访问 Direct Connect [位置](https://aws.amazon.com/directconnect/locations/) 部分或 [产品详情页面](https://aws.amazon.com/directconnect) 。或者，访问我们的 [入门页面](https://aws.amazon.com/directconnect/getting-started/) ，了解如何购买和部署 Direct Connect。

---

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/01/aws-client-vpn-concurrent-vpn-connections/](https://aws.amazon.com/about-aws/whats-new/2025/01/aws-client-vpn-concurrent-vpn-connections/)

**发布时间:** 2025-01-22

**厂商:** AWS

**类型:** 最新动态

---

# AWS Client VPN 宣布支持并发 VPN 连接 (concurrent VPN connections)

发布于: 2025 年 1 月 22 日 

今天，AWS 宣布并发 VPN 连接 (concurrent VPN connections) 功能在 AWS Client VPN 中正式可用。这一功能让您能同时安全连接到多个 Client VPN 连接，从而轻松访问不同工作环境的资源。  

AWS Client VPN 允许用户从任意地点安全远程连接到您的网络。以前，您一次只能连接到一个 VPN 配置 (VPN profile)，这限制了访问仅限于一个网络。要访问另一个网络，您需断开当前连接并重新连接到不同的 VPN 配置 (VPN profile)。借助此新功能，您可以同时连接多个 VPN 配置 (VPN profile)，而无需切换。例如，使用 AWS Client VPN 客户端的软件开发人员现在能并发连接到开发、测试和生产环境。这一功能支持无缝并行连接到所有所需环境，大幅提升了最终用户的生产力。  

此功能仅适用于 AWS 提供的 Client VPN 客户端版本 5.0+。您可以按照 [此处](https://aws.amazon.com/vpn/client-vpn-download/) 的步骤下载此版本。此功能和所需客户端版本在 AWS Client VPN 全面提供的所有 AWS 区域中免费提供。  

要了解更多关于 Client VPN 的信息：  

  * 访问 AWS Client VPN [产品页面](https://aws.amazon.com/vpn/)  
  * 阅读 AWS Client VPN [文档](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/what-is.html)

---

# AWS 在沙特阿拉伯王国宣布新边缘位置 (edge location)

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/01/new-edge-location-kingdom-saudi-arabia](https://aws.amazon.com/about-aws/whats-new/2025/01/new-edge-location-kingdom-saudi-arabia)

**发布时间:** 2025-01-24

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS 在沙特阿拉伯王国宣布新边缘位置 (edge location)

发表于：2025 年 1 月 24 日

亚马逊网络服务 (Amazon Web Services, AWS) 宣布在沙特阿拉伯王国扩展，通过在吉达推出一个新的 Amazon CloudFront 边缘位置 (edge location)。这个新的 AWS 边缘位置 (edge location) 带来了 Amazon CloudFront 的全部优势，这是一个安全、高度分布且可扩展的内容交付网络 (CDN)，用于以低延迟和高性能交付静态和动态内容、API 以及直播和点播视频。  
  
所有 Amazon CloudFront 边缘位置 (edge location) 都通过 AWS Shield Standard 获得保护，以抵御基础设施级别的 DDoS 威胁。AWS Shield Standard 使用始终在线的网络流量监控和内联缓解措施，来最小化应用程序的延迟和停机时间。您还可以为应用程序添加额外的安全层，通过启用 AWS Web Application Firewall (WAF) 来保护它们免受常见网络漏洞和机器人攻击。  
  
从这个边缘位置 (edge location) 交付的流量包含在中东区域的定价 (region pricing) 内。要了解更多关于 AWS 边缘位置 (edge location) 的信息，请查看 [CloudFront 边缘位置 (edge locations)](https://aws.amazon.com/cloudfront/features/)。

---

# AWS 网络负载均衡器 (Network Load Balancer) 现支持移除可用区 (Availability Zones)

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/02/aws-network-load-balancer-removing-availability-zones](https://aws.amazon.com/about-aws/whats-new/2025/02/aws-network-load-balancer-removing-availability-zones)  

**发布时间:** 2025-02-13  

**厂商:** AWS  

**类型:** WHATSNEW  

---  

# AWS 网络负载均衡器 (Network Load Balancer) 现支持移除可用区 (Availability Zones)  

发布日期: 2025 年 2 月 13 日  

今天，我们推出了在现有网络负载均衡器 (Network Load Balancer) 中移除可用区 (Availability Zones) 的功能。在此之前，客户可以向现有 NLB 添加可用区，但无法移除。现在，通过此功能，客户可以快速更改应用堆栈的位置，并在可用区之间迁移。  

随着业务需求的变化，例如并购、分拆、数据驻留合规要求，以及特定区域的容量考虑等场景，都可能需要移除现有 NLB 的可用区。使用此功能，客户可以通过更新启用子网列表来从 NLB 中移除一个或多个可用区 (Availability Zones)，操作方式包括使用弹性负载均衡 (Elastic Load Balancing) API、CLI 或控制台 (Console)。  

与任何删除操作类似，移除可用区 可能是一种潜在破坏性的操作。移除可用区 时，NLB 的分区弹性网络接口 (Elastic Network Interface) 将被删除；所有连接到该分区后端目标 (包括通过其他分区连接的客户端) 的活动连接将被终止；分区 IP (以及弹性 IP 地址 (Elastic IP addresses)) 将被释放，分区 DNS 名称将被删除，以及移除分区中的任何后端目标将变为“未使用”状态。请参考 [产品文档](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/availability-zones.html) 和 [AWS 博客文章](https://aws.amazon.com/blogs/networking-and-content-delivery/exploring-new-subnet-management-capabilities-of-network-load-balancer/) ，以获取安全使用此功能的指导建议。  

此功能适用于所有 [AWS 商业区域](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 以及 AWS GovCloud (US) 区域。

---

# AWS Network Firewall 引入自动域名列表 和 洞察

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/02/aws-network-firewall-automated-domain-lists](https://aws.amazon.com/about-aws/whats-new/2025/02/aws-network-firewall-automated-domain-lists)

**发布时间:** 2025-02-19

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Network Firewall 引入自动域名列表 和 洞察

发表于: 2025 年 2 月 19 日 

[AWS Network Firewall](https://aws.amazon.com/network-firewall/) 现在提供自动域名列表 (Automated Domain Lists) 和 洞察 (Insights) 功能，此功能增强了对网络流量的可见性，并简化了防火墙规则配置。该功能会分析过去 30 天的 HTTP 和 HTTPS 流量日志，并提供对频繁访问域名的洞察，从而根据观察到的网络流量模式快速创建规则。  
  
许多组织现在使用允许列表 (Allow-List) 策略来限制仅访问已批准的目的地。自动域名列表 (Automated Domain Lists) 可以减少识别必要域名、配置初始规则以及随着业务需求变化更新允许列表所需的时间和精力。该功能有助于快速识别合法流量，同时保持严格的默认拒绝姿态，从而在安全性和操作效率之间实现平衡。  
  
此功能在所有当前支持 [AWS Network Firewall](https://aws.amazon.com/network-firewall/) 的 [AWS 区域 (AWS Regions)](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 中可用。生成自动域名列表 (Automated Domain Lists) 和 洞察 (Insights) 不额外收费。  
  
要开始使用，请访问 AWS Network Firewall 控制台并为您的防火墙启用分析模式。有关更多信息，请参考 AWS Network Firewall 服务 [文档](https://docs.aws.amazon.com/network-firewall/latest/developerguide/firewall-creating.html)。

---

# Amazon Location Service 现已支持 AWS PrivateLink

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/02/amazon-location-service-supports-privatelink/](https://aws.amazon.com/about-aws/whats-new/2025/02/amazon-location-service-supports-privatelink/)

**发布时间:** 2025-02-25

**厂商:** AWS

**类型:** WHATSNEW

---

# Amazon Location Service 现已支持 AWS PrivateLink

发布于: 2025 年 2 月 25 日 

我们很高兴宣布，Amazon Location Service 现已支持 AWS PrivateLink (AWS PrivateLink) 集成，这使客户能够在他们的虚拟私有云 (VPC) 与 Amazon Location Service 之间建立私有连接，而数据无需通过公共互联网。  
  
通过这一新功能，客户现在可以通过其 VPC 中的私有 IP 地址访问 Amazon Location Service API，从而显著提升其安全姿态。这种集成通过消除对互联网网关、NAT 设备或公共 IP 地址的需求，简化了网络架构，同时通过将所有流量保持在 AWS 网络内，帮助客户满足严格的监管和合规要求。  
  
为 Amazon Location Service 设置 AWS PrivateLink 非常简单。客户可以通过 AWS Management Console 或 AWS Command Line Interface (AWS CLI) 命令创建接口 VPC 端点。一旦配置完成，应用可以立即使用私有 IP 地址访问 Amazon Location Service API，所有流量都在 AWS 网络内保持安全。  
  
要了解更多关于将 AWS PrivateLink 与 Amazon Location 一起使用的信息，请参阅 [Amazon Location Service 开发者指南](https://docs.aws.amazon.com/location/latest/developerguide/privatelink-interface-endpoints.html)。

---

# Amazon API Gateway 现已在更多区域支持 HTTP APIs、mTLS、多级基路径映射和 WAF

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-api-gateway-http-apis-mtls-multi-level-base-path-mappings-waf-additional-regions](https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-api-gateway-http-apis-mtls-multi-level-base-path-mappings-waf-additional-regions)  

**发布时间:** 2025-03-03  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon API Gateway 现已在更多区域支持 HTTP APIs、mTLS、多级基路径映射和 WAF  

发布日期: 2025 年 3 月 3 日  

[Amazon API Gateway](https://aws.amazon.com/api-gateway/) (APIGW) 现已在以下额外区域支持 HTTP APIs (HTTP Application Programming Interfaces) 的所有功能，以及在 REST APIs 上支持 mTLS (Mutual Transport Layer Security) 和多级基路径映射：中东 (阿联酋)、亚太 (雅加达)、亚太 (大阪)、亚太 (海得拉巴)、亚太 (墨尔本)、欧洲 (苏黎世)、欧洲 (西班牙)、以色列 (特拉维夫) 和加拿大西部 (卡尔加里)。此外，AWS Web Application Firewall (WAF) 对于 REST APIs 现已在两个额外区域可用：亚太 (吉隆坡) 和加拿大西部 (卡尔加里)。  
  
HTTP APIs 通过更简单的用户界面简化了无服务器应用的 API 开发，该界面支持 OAuth 2.0 (OAuth 2.0) 和自动部署。mTLS 通过在 APIGW 验证基于 x509 证书的身份来提升安全性。多级基路径映射允许基于自定义域名路径中的段路由请求，支持基于路径的版本管理和流量重定向。集成 AWS WAF 可通过可配置规则保护 API 免受常见网络攻击，这些规则可允许、阻塞或监控网络请求。  
  
要了解更多信息，请参阅 [API Gateway 开发者指南](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)。

---

# 应用负载均衡器 宣布与 Amazon VPC IP 地址管理器 整合

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/application-load-balancer-integration-vpc-ipam/](https://aws.amazon.com/about-aws/whats-new/2025/03/application-load-balancer-integration-vpc-ipam/)  

**发布时间:** 2025-03-07  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# 应用负载均衡器 宣布与 Amazon VPC IP 地址管理器 整合  

发布日期: 2025 年 3 月 7 日  

AWS 应用负载均衡器 (Application Load Balancer) 现在允许客户为负载均衡器节点提供一个公网 IPv4 地址池，用于 IP 地址分配。客户可以配置一个公网 IP 地址管理器 (IPAM) 池，该池可以包括客户自带 IP (Bring Your Own IP) 地址，或者由 Amazon 提供的连续 IPv4 地址块。  
  
借助此功能，客户可以通过在公网 IPAM 池中使用自带 IP 来优化公网 IPv4 成本。客户还可以通过在公网 IPAM 池中使用 Amazon 提供的连续 IPv4 地址块，来简化企业允许列表和运营操作。应用负载均衡器的 IP 地址来自 IPAM 池，并在公网 IPAM 池耗尽时自动切换到 AWS 管理的 IP 地址。这种智能切换在缩放事件中最大化了服务可用性。  
  
此功能可在 [所有商业 AWS 区域](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 和 [AWS GovCloud (US)](https://aws.amazon.com/govcloud-us/) 区域中使用，前提是 Amazon VPC IP 地址管理器 (Amazon VPC IPAM) 已可用。要了解更多信息，请参阅 [应用负载均衡器 文档](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/application-load-balancers.html#ip-pools)。

---

# Amazon Route 53 Traffic Flow 引入新的视觉编辑器 (visual editor) 以改进 DNS 策略编辑

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-route-53-traffic-flow-visual-editor-improve-dns-policy-editing](https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-route-53-traffic-flow-visual-editor-improve-dns-policy-editing)  

**发布时间:** 2025-03-13  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon Route 53 Traffic Flow 引入新的视觉编辑器以改进 DNS 策略编辑  

发布时间: 2025 年 3 月 13 日  

Amazon Route 53 Traffic Flow (Amazon Route 53 Traffic Flow) 现在提供了一个增强的用户界面，用于改进 DNS 流量策略编辑。Route 53 Traffic Flow 是一个网络流量管理功能 (network traffic management feature)，它通过在网页浏览器中提供交互式的 DNS 策略管理流程图 (DNS policy management flow chart)，简化了在大型和复杂配置中创建和维护 DNS 记录的过程。借助此版本发布，您可以使用视觉编辑器的 (visual editor) 新功能，更轻松地理解和更改用户与端点之间的流量路由方式。  
  
现在，Traffic Flow 通过将配置移动到新的侧边栏、提供撤销/重做按钮 (undo/redo button)，以及引入一个新的文本编辑器来编辑 JavaScript Object Notation (JSON) 文件，直接在浏览器中操作，从而提供了一种更清晰的方式来构建针对多个端点和多种路由方法的 DNS 路由策略。该 JSON 编辑器还包括语法高亮 (syntax highlighting)，并可与新的“暗模式” (Dark Mode) 主题结合使用，以显示策略编辑的位置。  
  
新的 Traffic Flow 体验在全球范围内可用，但不包括 AWS GovCloud 和 Amazon Web Services in China。Traffic Flow 的定价信息可在此处 [查看](https://aws.amazon.com/route53/pricing/) ，这些增强功能无需额外费用。要了解更多关于使用 Traffic Flow 的信息，请访问我们的 [文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/traffic-flow.html) 或查看 [此博客文章](https://aws.amazon.com/blogs/networking-and-content-delivery/managing-global-aws-local-zones-applications-with-amazon-route53-geoproximity-routing/)。

---

# AWS 宣布在葡萄牙里斯本开设新的 AWS Direct Connect 位置

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/aws-direct-connect-location-lisbon-portugal](https://aws.amazon.com/about-aws/whats-new/2025/03/aws-direct-connect-location-lisbon-portugal)  

**发布时间:** 2025-03-14  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS 宣布在葡萄牙里斯本开设新的 AWS Direct Connect 位置  

发布日期: 2025 年 3 月 14 日  

今天，AWS 宣布在葡萄牙里斯本附近的 Equinix LS1 数据中心开设一个新的 AWS Direct Connect（AWS Direct Connect）位置。通过在新的位置将您的网络连接到 AWS，您可以获得对所有公共 AWS 区域（AWS Regions）（除中国区域外）、AWS GovCloud 区域，以及 [AWS Local Zones](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) 的私有直接访问。此位置是葡萄牙的第一个 AWS Direct Connect 位置。新位置提供专用的 10 Gbps 和 100 Gbps 连接，并支持 MACsec 加密。  
  
AWS Direct Connect 服务让您能够在 AWS 与您的数据中心、办公室或共址环境之间建立私有物理网络连接。这些私有连接比通过公共互联网连接提供更稳定的网络体验。  
  
有关全球超过 145 个 AWS Direct Connect 位置的更多信息，请访问 AWS Direct Connect [位置](https://aws.amazon.com/directconnect/locations/) 部分或 [产品详情页面](https://aws.amazon.com/directconnect)。或者，访问我们的 [入门页面](https://aws.amazon.com/directconnect/getting-started/)，了解如何购买和部署 AWS Direct Connect。

---

# AWS Verified Access 获得 FedRAMP High 和 Moderate 授权

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/aws-verified-access-fedramp-high-moderate-authorization](https://aws.amazon.com/about-aws/whats-new/2025/03/aws-verified-access-fedramp-high-moderate-authorization)  

**发布时间:** 2025-03-14  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS Verified Access 获得 FedRAMP High 和 Moderate 授权  

发表于: 2025 年 3 月 14 日  

AWS Verified Access 是 AWS GovCloud (US) 区域中的 FedRAMP High 授权服务，以及 AWS US East 和 US West 商业区域中的 FedRAMP Moderate 授权服务。联邦机构、公共部门组织以及其他需要 FedRAMP (Federal Risk and Authorization Management Program) 合规的企业现在可以使用 AWS Verified Access 来实现对企业 HTTP、非 HTTP 应用程序以及基础设施资源的安全的无 VPN 访问。基于 [AWS Zero Trust (AWS Zero Trust)](https://aws.amazon.com/security/zero-trust/) 原则构建，您可以使用 Verified Access 实现一个可从任何地方工作的模型，并增加安全性和可扩展性。  
  
AWS Verified Access 允许管理员基于用户的身份和设备状态定义细粒度的访问策略。它会对每个连接请求进行评估，并持续监控活跃连接，在访问策略中指定的安全要求未满足时终止连接。例如，您可以集中定义访问策略，仅授予财务组使用合规和管理设备的认证用户访问财务应用程序。此外，您还可以使用 Verified Access 启用对非 HTTP(S) 应用程序和资源的访问，例如运行在 EC2 (EC2) 实例上的数据库、SAP 和 git 仓库。Verified Access 通过允许您从单一界面集中创建、归组和管理具有类似安全需求的所有应用程序和资源的访问策略，从而简化安全操作。  
  
要了解更多关于 AWS Verified Access 的信息，[访问产品页面](https://aws.amazon.com/verified-access/) 。

---

# AWS Client VPN 增加授权规则和路由配额

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/aws-client-vpn-authorization-rules-route-quotas](https://aws.amazon.com/about-aws/whats-new/2025/03/aws-client-vpn-authorization-rules-route-quotas)  

**发布时间:** 2025-03-18  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS Client VPN 增加授权规则和路由配额  

发布时间: 2025 年 3 月 18 日  

今天，AWS 宣布为 AWS Client VPN (AWS Client VPN) 增加配额，将每目标网络关联 (target network association) 的路由扩展到 100 个，以及每端点 (endpoint) 的授权规则扩展到 200 个。  

AWS Client VPN 允许您安全地管理 VPN 连接的网络路由和访问控制。以前，默认配额 (default quota) 为每关联 (association) 10 个路由和每端点 50 个授权规则。随着此次配额增加，您现在可以配置最多 100 个路由每关联和 200 个规则每端点。例如，具有分布式架构 (distributed architectures) 的企业可以为开发、暂存和生产环境中的多个子网 (subnets) 定义特定路由路径，从而提供更大的灵活性和对网络流量流的粒度控制。  

这些新配额是默认配置 (default configurations)，并且可以调整到更高限制。这些默认配额会自动应用于所有新旧 Client VPN 端点 (endpoint)。此增强功能在所有 AWS 区域 (AWS Regions) 中免费提供，AWS Client VPN 在这些区域已全面可用。  

要了解更多关于 Client VPN 的信息：  
  * 阅读 AWS Client VPN [配额页面](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/limits.html)  
  * 访问 AWS Client VPN [产品页面](https://aws.amazon.com/vpn/)  
  * 阅读 AWS Client VPN [文档](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/what-is.html)

---

# AWS PrivateLink 跨区域连接性 (cross-region connectivity) 现已在 6 个额外区域可用

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/aws-privatelink-cross-region-connectivity-6-additional-regions/](https://aws.amazon.com/about-aws/whats-new/2025/03/aws-privatelink-cross-region-connectivity-6-additional-regions/) 

**发布时间:** 2025-03-18

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS PrivateLink 跨区域连接性现已在 6 个额外区域可用

发布时间: 2025 年 3 月 18 日 

AWS PrivateLink 现已在以下额外区域支持原生跨区域连接性 (cross-region connectivity)：Canada West (Calgary)、Europe (Zurich)、Middle East (UAE) 以及 Asia Pacific (Hyderabad, Jakarta, Melbourne)。

此功能发布使客户能够通过接口端点 (Interface endpoints) 连接到其他 AWS 区域中托管的 VPC 端点 (VPC endpoint) 服务，前提是这些区域位于同一 AWS 分区 (partition)。作为服务提供者，您可以为所有现有和即将推出的 AWS 区域中的客户启用对您的 VPCE 服务 (VPCE service) 的访问，而无需在每个区域设置额外的基础设施。作为服务消费者，您可以私密连接到其他 AWS 区域中的 VPCE 服务，而无需设置跨区域对等连接 (cross-region peering) 或通过公共互联网暴露数据。启用了跨区域的 VPCE 服务可以通过接口端点在您的 VPC 中的私有 IP 地址访问，从而实现更简单、更安全的区域间连接。

要了解此功能的定价，请查看 [AWS PrivateLink 定价页面](https://aws.amazon.com/privatelink/pricing/)。要了解更多信息，请阅读我们的 [博客](https://aws.amazon.com/blogs/networking-and-content-delivery/introducing-cross-region-connectivity-for-aws-privatelink/) 和访问 [*AWS PrivateLink*](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html) 在 Amazon VPC 开发者指南中。

---

# AWS 网络防火墙 (AWS Network Firewall) 推出新的流量管理功能

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/aws-network-firewall-flow-management-feature/](https://aws.amazon.com/about-aws/whats-new/2025/03/aws-network-firewall-flow-management-feature/)

**发布时间:** 2025-03-20

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS 网络防火墙 推出新的流量管理功能

发表于：2025 年 3 月 20 日 

今天，AWS 宣布为 AWS 网络防火墙 推出一个新的流量管理功能，该功能让客户能够识别和控制活跃的网络流量 (network flows)。这个功能引入了两个关键功能：流量捕获 (Flow Capture)，它允许捕获活跃流量的即时快照，以及流量刷新 (Flow Flush)，它能选择性地终止特定连接。通过这些新能力，客户现在可以根据源/目标 IP 地址、端口 (ports) 和协议 (protocols) 等标准查看和管理活跃流量，从而为网络流量提供更强的控制。  
  
这个新功能有助于客户在更新防火墙规则 (firewall rules) 时保持一致的安全策略 (security policies)，并在安全事件中实现快速响应。网络管理员现在可以轻松验证安全配置，并确保所有流量都符合当前策略。该流量管理功能在排查网络问题和隔离可疑流量 (suspicious traffic) 期间特别有用。通过对活跃网络流量的细粒度控制，AWS 网络防火墙 提升了客户维护安全且高效网络环境的能力。  
  
新的流量管理功能已在所有支持 AWS 网络防火墙 的区域可用，让客户在其全球基础设施中受益。  
  
客户可以免费开始使用流量捕获 和 流量刷新。要开始使用，请访问 [AWS 网络防火墙 文档](https://docs.aws.amazon.com/network-firewall/latest/developerguide/what-is-aws-network-firewall.html)、探索 [网络防火墙 API 参考指南](https://docs.aws.amazon.com/network-firewall/latest/APIReference/Welcome.html) 中的新 API，或在 [产品页面](https://aws.amazon.com/network-firewall/) 上了解更多关于 AWS 网络防火墙 的信息。

---

# Amazon EventBridge Scheduler 现已支持 AWS PrivateLink

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-eventbridge-scheduler-privatelink/](https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-eventbridge-scheduler-privatelink/)

**发布时间:** 2025-03-25

**厂商:** AWS

**类型:** WHATSNEW

---

# Amazon EventBridge Scheduler 现已支持 AWS PrivateLink

发布日期: 2025 年 3 月 25 日 

Amazon EventBridge Scheduler 现已支持 [私有链接 (AWS PrivateLink)](https://aws.amazon.com/privatelink/)，让您能够在 Amazon 虚拟私有云 (VPC) 内访问 Scheduler，而无需使用公共互联网。此功能在使用私有子网访问 EventBridge Scheduler 时，消除了对互联网网关、防火墙规则或代理服务器的需求。  
  
使用 Amazon EventBridge Scheduler，您可以创建数十亿个计划事件和任务，这些事件和任务可在 270 多个 AWS 服务中运行，而无需配置或管理基础架构。您可以为特定日期和时间设置一次性计划，或使用 cron 和 rate 表达式创建重复计划，支持时区和夏令时。在 EventBridge Scheduler 中添加 [私有链接 (AWS PrivateLink)](https://aws.amazon.com/privatelink/) 支持后，当您从 VPC 内向 Scheduler 发出 API 调用时，可以减少创建和管理计划所需的基础架构。  
  
EventBridge Scheduler 的 [私有链接 (AWS PrivateLink)](https://aws.amazon.com/privatelink/) 支持可在所有提供 EventBridge Scheduler 的 AWS 区域中使用。使用此功能不会产生额外成本，但标准 AWS PrivateLink 定价适用。  
  
有关 [私有链接 (AWS PrivateLink)](https://docs.aws.amazon.com/en_us/vpc/latest/privatelink/privatelink-access-aws-services.html) 配置说明，请参阅 [AWS PrivateLink 文档](https://docs.aws.amazon.com/en_us/vpc/latest/privatelink/privatelink-access-aws-services.html)。要了解更多关于 Amazon EventBridge Scheduler 及其功能的信息，请参阅 [EventBridge 文档](https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html)。

---

# Amazon Application Recovery Controller 宣布 AWS FIS 针对可用区自动转移 (zonal autoshift) 的恢复操作

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-application-recovery-controller-fis-recovery-action/](https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-application-recovery-controller-fis-recovery-action/)  

**发布时间:** 2025-03-26  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon Application Recovery Controller 宣布 AWS FIS 针对可用区自动转移 (zonal autoshift) 的恢复操作  

发布时间: 2025 年 3 月 26 日  

AWS 故障注入服务 (FIS) 现已支持针对 Amazon 应用恢复控制器 (ARC) 的可用区自动转移 (zonal autoshift) 恢复操作。恢复操作是一种新的 FIS 操作类型，允许客户演示 AWS 在可用性事件期间的响应方式。例如，当 AWS 检测到一个可用区 (AZ) 中存在潜在的基础设施问题（如电力或网络中断）时，可用区自动转移 (zonal autoshift) 会自动将流量从该可用区 (AZ) 转移走。通过新的 FIS 恢复操作，已启用可用区自动转移 (zonal autoshift) 的客户可以运行 FIS 的可用区可用性: 电力中断场景，以模拟一个可用区 (AZ) 完全电力中断的预期症状，并演示 AWS 如何触发可用区自动转移 (zonal autoshift)。这让客户能够调整其监控和恢复流程，从而提升弹性并改善应用可用性。  
  
FIS 的可用区可用性: 电力中断场景现在不仅包括电力中断症状，还包含了从可用区自动转移 (zonal autoshift) 中恢复的预期过程，包括分区计算 (如 Amazon EC2、EKS 和 ECS) 丢失、RDS 和 ElastiCache 的故障转移等。运行该场景让客户测试并增强信心，确保其应用在可用区 (AZ) 不可用时能按预期响应。  
  
要开始使用，请从 FIS 场景库中选择可用区可用性: 电力中断场景。该操作可在所有支持 FIS 和可用区自动转移 (zonal autoshift) 的 AWS 区域使用，包括 AWS GovCloud (US) 区域。要了解更多信息，请访问 [文档](https://docs.aws.amazon.com/fis/latest/userguide/fis-actions-reference.html#fis-actions-recovery)。

---

# Amazon Route 53 Profiles 现已支持互联网协议版本 6 (IPv6) 服务端点

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-route-53-profiles-ipv6-service-endpoints](https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-route-53-profiles-ipv6-service-endpoints)

**发布时间:** 2025-03-26

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon Route 53 Profiles 现已支持互联网协议版本 6 (IPv6) 服务端点

发布时间: 2025 年 3 月 26 日  

Amazon Route 53 Profiles 引入了对 Route 53 Profiles API 端点的双栈支持，让您能够使用 互联网协议版本 6 (IPv6)、互联网协议版本 4 (IPv4) 或双栈客户端进行连接。原有支持 IPv4 的 Route 53 Profiles 端点将继续可用，以确保向后兼容。  
  
Route 53 Profiles 让您轻松创建和管理一个或多个与 VPC (Virtual Private Cloud) 相关的 DNS (Domain Name System) 设置配置，例如私有托管区域和 Route 53 Resolver 规则，并将其在多个 VPC 和 AWS 账户之间共享。转向 互联网协议版本 6 (IPv6) 的紧迫性源于互联网的持续增长，这导致了 互联网协议版本 4 (IPv4) 地址的短缺。通过在 Route 53 Profiles 端点上同时支持 IPv4 和 IPv6 客户端，您可以逐步从 IPv4 过渡到基于 IPv6 的系统和应用，而无需一次性全部切换。这有助于您满足 IPv6 合规性要求，并消除使用昂贵网络设备进行 IPv4 和 IPv6 地址转换的需要。  
  
IPv6 在 Route 53 Profiles 上的支持已适用于所有 AWS 商用区域和 AWS GovCloud (US) 区域中 Route 53 Profiles 可用的区域。查看 [此处](https://docs.aws.amazon.com/general/latest/gr/r53.html#r53_region) 以获取完整区域列表。您可以通过 AWS CLI 或 [AWS Management Console](https://console.aws.amazon.com/rds/home) 开始使用此功能。要了解更多关于 Route 53 Profiles 的信息，请访问 Route 53 [文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/profiles.html)。要了解更多关于定价的信息，请访问 [Route 53 定价页面](https://aws.amazon.com/route53/pricing/)。

---

# AWS Network Manager 和 AWS Cloud WAN 现已支持 AWS PrivateLink 和 IPv6

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/aws-network-manager-cloud-wan-privatelink-ipv6](https://aws.amazon.com/about-aws/whats-new/2025/03/aws-network-manager-cloud-wan-privatelink-ipv6)  

**发布时间:** 2025-03-27  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS Network Manager 和 AWS Cloud WAN 现已支持 AWS PrivateLink 和 IPv6  

发表于：2025 年 3 月 27 日  

AWS Network Manager 和 AWS Cloud WAN 现已支持基于 AWS PrivateLink 和 IPv6 的连接到这些服务的管理端点。使用 AWS PrivateLink，客户现在可以在 AWS 网络上私密访问 AWS Network Manager 或 AWS Cloud WAN，而无需通过公共互联网。此外，客户现在可以使用双栈端点通过 IPv6 访问这些服务。  

借助 AWS Cloud WAN，您可以使用中央仪表板和网络策略来创建一个跨越多个位置和网络的全球网络，从而允许您使用相同的技术配置和管理不同的网络。AWS Cloud WAN 中央仪表板由 AWS Network Manager 提供支持，它生成网络的完整视图，帮助您监控网络健康、安全性和性能。AWS Network Manager 可降低管理跨越 AWS 和本地位置的全球网络的操作复杂性。以前，您只能使用公共 IPv4 端点访问 AWS Cloud WAN 和 AWS Network Manager。通过此次发布，您现在可以私密访问这些服务的 API/CLI，而无需通过公共互联网。此外，这些服务现在支持 IPv6 端点。  

要了解更多关于 AWS Network Manager 的信息，请参考 [文档](https://docs.aws.amazon.com/network-manager/latest/tgwnm/what-are-global-networks.html#nm-privatelink) ，以及关于 AWS Cloud WAN 的信息，请参考 [文档](https://docs.aws.amazon.com/network-manager/latest/cloudwan/what-is-cloudwan.html#cloudwan-privatelink) 。

---

# Amazon VPC IP 地址管理器现已在两个额外 AWS 区域可用

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-vpc-ip-address-manager-two-additional-regions/](https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-vpc-ip-address-manager-two-additional-regions/)  

**发布时间:** 2025-03-27  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon VPC IP 地址管理器现已在两个额外 AWS 区域可用  

发布时间: 2025-03-27   

Amazon Virtual Private Cloud IP 地址管理器 [Amazon VPC IPAM (Amazon VPC IP Address Manager)] 可以让您更轻松地为 AWS 工作负载规划、跟踪和监控 IP 地址，现在已在亚太区域 (Thailand) 和墨西哥 (Central) 区域可用。  

Amazon VPC IPAM 允许您根据路由和安全需求轻松组织 IP 地址，并设置简单的业务规则来管理 IP 地址分配。通过使用 VPC IPAM，您可以自动为 Amazon VPC 和 VPC 子网 (VPC Subnets) 分配 IP 地址，从而无需使用基于电子表格或自制 IP 地址规划应用，这些应用可能难以维护且耗时。  

通过此次扩展，Amazon VPC IPAM 已在所有 AWS 区域 (AWS Regions) 可用，包括中国 (北京，由 Sinnet 运营)、中国 (宁夏，由 NWCD 运营) 以及 AWS GovCloud (US) 区域。  

要了解更多关于 IPAM 的信息，请查看 [IPAM 文档](https://docs.aws.amazon.com/vpc/latest/ipam/what-it-is-ipam.html)。有关定价详情，请参考 [Amazon VPC 定价页面](https://aws.amazon.com/vpc/pricing/) 中的 IPAM 标签。

---

# AWS Network Firewall 新增 pass action 规则警报和 JA4 过滤

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/aws-network-firewall-pass-action-rule-alerts-ja4-filtering](https://aws.amazon.com/about-aws/whats-new/2025/03/aws-network-firewall-pass-action-rule-alerts-ja4-filtering)  

**发布时间:** 2025-03-27  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS Network Firewall 新增 pass action 规则警报和 JA4 过滤  

发表于：2025 年 3 月 27 日  

今天，AWS 宣布为 AWS Network Firewall 新增功能：生成匹配 pass action 规则 (Pass Action Rule) 流量的警报能力，以及在防火墙规则中支持 JA4 指纹识别 (JA4 Fingerprinting)。AWS Network Firewall 是一个有状态的、托管的网络防火墙和入侵检测与预防服务，用于您的虚拟私有云 (VPC)。这些新功能增强了网络流量的安全性和可见性，让您能够实现更细粒度的控制和改进的威胁检测。  
  
生成匹配 pass action 规则流量的警报日志事件的能力，能让您在无需在 pass action 规则前添加警报动作规则的情况下，获得对网络流量的增强可见性。这有助于您检测异常或潜在安全问题，这些流量原本可能会被允许而不受额外审查。JA4 过滤规则 (JA4 Filtering) 让 AWS Network Firewall 能够基于 JA4 指纹识别分析网络流量，JA4 指纹识别用于识别客户端和服务器应用。这功能允许更精确的流量识别和控制，帮助您更好地保护网络免受潜在威胁。  
  
pass action 规则警报和 JA4 过滤规则已在所有提供 AWS Network Firewall 的 AWS 区域可用。要查看 AWS Network Firewall 可用的区域，请访问 [AWS 区域表](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/)。  
  
要了解这些新功能的更多信息以及如何在您的 AWS Network Firewall 设置中实施它们，请访问 [AWS Network Firewall 文档](https://docs.aws.amazon.com/network-firewall/latest/developerguide/what-is-aws-network-firewall.html)。您可以立即开始使用这些功能，以提升网络安全态势并获得更深入的 VPC 流量模式洞察。

---

# Amazon EC2 现已支持更多带宽和巨型帧 (Jumbo Frames) 到选定目的地

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-ec2-bandwidth-jumbo-frames](https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-ec2-bandwidth-jumbo-frames)  

**发布时间:** 2025-03-28  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon EC2 现已支持更多带宽和巨型帧到选定目的地  

发布时间: 2025 年 3 月 28 日  

Amazon EC2 现已支持高达实例的完整带宽，用于区域间 VPC (VPC) 对等连接流量和 AWS Direct Connect。此外，EC2 还支持巨型帧 (Jumbo Frames) 最大达 8500 字节，用于跨区域 VPC 对等连接。在此之前，EC2 实例的出口带宽限于聚合带宽限制的 50%，适用于拥有 32 个或更多 vCPUs 的实例，而较小实例限于 5 Gbps。跨区域对等连接支持最大 1500 字节。现在，用户可以将带宽从 EC2 发送到其他区域或 AWS Direct Connect，达到实例基准规格或 5 Gbps 中的较大值，并且用户可以在对等 VPC 中跨区域使用巨型帧。  
  
用户在区域间传输数据，或从 EC2 通过 AWS Direct Connect 连接到本地网络 (on-premises) 时，现在可以访问实例的完整带宽功能。在此之前，向非同一区域的目的地发送流量时，带宽有限制。此次更新移除了针对 AWS 区域间目的地和通过 AWS Direct Connect 到本地网络的限制，从而实现更快的传输。此外，支持巨型帧用于对等连接，使得发送大容量数据比以往更快。  
  
此功能适用于所有 AWS 商业区域、AWS GovCloud (US) 区域，以及由 Sinnet 运营的 Amazon Web Services China (Beijing) 区域和由 NWCD 运营的 Amazon Web Services China (Ningxia) 区域。用户无需进行额外更改即可使用此功能。要了解更多关于 EC2 带宽功能的信息，请查看我们的 [用户指南](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-network-bandwidth.html)。

---

# API Gateway 推出对双栈 (dual-stack) 端点的支持

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/api-gateway-dual-stack-ipv4-ipv6-endpoints/](https://aws.amazon.com/about-aws/whats-new/2025/03/api-gateway-dual-stack-ipv4-ipv6-endpoints/)

**发布时间:** 2025-03-31

**厂商:** AWS

**类型:** WHATSNEW

---
# API Gateway 推出对双栈 (dual-stack) 端点的支持

发布于：2025 年 3 月 31 日 

Amazon API Gateway (APIGW) 引入了对所有端点类型、自定义域名和 APIGW 管理 API 的双栈支持 (dual-stack)。您现在可以将 REST API、HTTP API 或 WebSocket API，以及自定义域名，配置为同时接受 IPv6 客户端的调用，同时保留现有的 IPv4 支持。您还可以从双栈客户端调用 APIGW 管理 API。  

通过同时支持 IPv4 和 IPv6 客户端，您能够逐步从 IPv4 环境过渡到 IPv6 环境，而无需一次性全部切换。这有助于满足 IPv6 合规要求，并避免 IPv4 地址限制。此支持无需额外收费。  

此功能现已在所有 API Gateway 商业区域和 AWS GovCloud (US) 区域可用。如需了解更多信息，请参阅 [API Gateway 开发者指南](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-ip-address-type.html) 和 [IPv6 on AWS](https://docs.aws.amazon.com/whitepapers/latest/ipv6-on-aws/internet-protocol-version-6.html)。

---

# AWS 宣布在希腊雅典开设新的 AWS Direct Connect 位置

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/03/aws-direct-connect-location-athens-greece](https://aws.amazon.com/about-aws/whats-new/2025/03/aws-direct-connect-location-athens-greece)  

**发布时间:** 2025-03-31  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS 宣布在希腊雅典开设新的 AWS Direct Connect 位置  

发表于: 2025 年 3 月 31 日  

今天，AWS 宣布在希腊雅典附近的 Digital Realty ATH3 数据中心开设一个新的 AWS Direct Connect (AWS Direct Connect) 位置。通过在新位置将您的网络连接到 AWS，您将获得对所有公共 AWS 区域 (AWS Regions) （除中国区域外）、AWS GovCloud 区域 (AWS GovCloud Regions) 以及 [本地扩展区域 (AWS Local Zones)](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) 的私有直接访问。此位置是希腊的第一个 AWS Direct Connect 位置。该 Direct Connect 位置提供专用的 10 Gbps 和 100 Gbps 连接，并支持 MACsec 加密 (MACsec encryption)。  
  
AWS Direct Connect 服务让您能够在 AWS 和您的数据中心、办公室或共址环境之间建立私有物理网络连接。这些私有连接可提供比通过公共互联网连接更稳定的网络体验。  
  
有关全球超过 147 个 Direct Connect 位置的更多信息，请访问 Direct Connect [位置](https://aws.amazon.com/directconnect/locations/) 部分或 [产品详情页面](https://aws.amazon.com/directconnect)。或者，访问我们的 [入门页面](https://aws.amazon.com/directconnect/getting-started/)，以了解如何购买和部署 Direct Connect。

---

# 宣布 Amazon VPC Route Server 的通用可用性

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-vpc-route-server/](https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-vpc-route-server/)  

**发布时间:** 2025-04-01  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# 宣布 Amazon VPC Route Server 的通用可用性  

发表于: 2025 年 4 月 1 日  

AWS 宣布 Amazon VPC (Virtual Private Cloud) 的 VPC 路由服务器 (VPC Route Server) 的通用可用性，以简化 Amazon VPC 中的虚拟设备之间的动态路由。VPC 路由服务器 (VPC Route Server) 允许您通过边界网关协议 (BGP) 从虚拟设备中发布路由信息，并动态更新与子网和互联网网关关联的 VPC 路由表。  

在此功能发布之前，您需要创建自定义脚本或使用带有覆盖网络的虚拟路由器来动态更新 VPC 路由表。VPC 路由服务器 (VPC Route Server) 消除了创建和维护覆盖网络或自定义脚本的操作开销，并提供了一个托管解决方案，用于在路由表中动态更新路由。通过 VPC 路由服务器 (VPC Route Server)，您可以在 VPC 中部署端点，并将它们与虚拟设备对等，以使用 BGP 发布路由。路由服务器 (VPC Route Server) 会使用标准 BGP 属性过滤这些接收到的路由，并将选定的路由传播到指定的路由表。这让您轻松动态更新路由，并快速缓解设备故障或其他问题。  

VPC 路由服务器 (VPC Route Server) 在以下 AWS 区域可用：美国东部 (弗吉尼亚)、美国东部 (俄亥俄)、美国西部 (俄勒冈)、欧洲 (爱尔兰)、欧洲 (法兰克福)和亚太 (东京)。  

有关更多信息，请参阅 [VPC 路由服务器文档](https://docs.aws.amazon.com/vpc/latest/userguide/dynamic-routing-route-server.html) 。

---

---
# Amazon CloudFront 支持使用 CloudFront Functions 修改 VPC Origin

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-cloudfront-vpc-origin-modification-functions/](https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-cloudfront-vpc-origin-modification-functions/)  

**发布时间:** 2025-04-02  

**厂商:** AWS  

**类型:** WHATSNEW  

---
# Amazon CloudFront 支持使用 CloudFront Functions 修改 VPC Origin

发布日期: 2025 年 4 月 2 日  

2024 年 11 月，CloudFront Functions (CloudFront Functions) 引进了源修改功能 (origin modifications)，让您能够根据请求条件动态更改源服务器 (origin servers)。从今天起，您可以将此功能应用于 VPC Origins (VPC Origins) 和源组 (origin groups)，从而为通过 CloudFront 交付的应用程序创建更复杂的路由策略 (routing policies)。  
  
现在，您可以创建动态路由策略，通过提供源 ID 将单个请求定向到任何源，包括 VPC Origins。通过这种方式，例如，您可以设置权重来自动将一定比例的流量路由到多个后端服务，从而将每个请求发送到不同应用程序，而无需更新分发配置 (distribution configuration)。此外，您还可以动态创建新的源组，并设置多个源及其故障转移标准 (failover criteria)。例如，您可以基于查看者位置 (viewer location) 或请求头 (request headers) 自定义故障转移逻辑，以更新主源和备用源，确保查看者获得最低延迟。  
  
这些功能现在在 CloudFront Functions 中免费提供。更多信息，请参阅 [CloudFront 开发者指南](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/helper-functions-origin-modification.html)。有关源修改的使用示例，请查看我们的 [GitHub 示例仓库](https://github.com/aws-samples/amazon-cloudfront-functions/tree/main/select-origin-based-on-country)。

---

# Amazon Route 53 在 AWS GovCloud (US) 区域中添加公共权威 DNS 服务

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-route-53-public-authoritative-dns-aws-govcloud-us-regions](https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-route-53-public-authoritative-dns-aws-govcloud-us-regions)  

**发布时间:** 2025-04-04  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon Route 53 在 AWS GovCloud (US) 区域中添加公共权威 DNS 服务  

发布于：2025 年 4 月 4 日  

Amazon Route 53 的公共托管区域 (Hosted Zones) 权威 DNS 服务现已在 AWS GovCloud (US-East 和 US-West) 区域中正式发布。随着今天的发布，依赖于公共 DNS 的 AWS 客户和 AWS 合作伙伴可以在 AWS GovCloud (US) 区域中使用该服务，并利用 Route 53 在商业 AWS 区域中的大部分功能。  
  
之前，客户使用来自商业 AWS 区域的 Route 53 权威 DNS 来路由流量到其在 AWS GovCloud (US) 区域中的应用。现在，您可以从 AWS GovCloud (US) 区域内的位置为您的公共托管区域提供 DNS 查询服务，而不依赖于商业 AWS 区域账户。功能包括权威 DNS 查询日志、DNSSEC (DNS Security Extensions) 签名支持在 AWS GovCloud (US) 公共托管区域上，以及对所有 Route 53 路由类型（除 IP 基于路由外）的支持。它还包括指向以下其他 AWS 服务的别名记录 (Alias Records)：Amazon API Gateway、Amazon S3、Amazon VPC 端点、AWS Elastic Beanstalk 和 Elastic Load Balancing (ELB) 负载均衡器。  
  
在 AWS GovCloud (US) 区域中使用 Route 53 入门非常简单。所有 AWS GovCloud (US) 区域的客户都可以通过 AWS Management Console 和 API 在 AWS GovCloud (US-West) 区域中使用 Route 53 权威 DNS。如需更多信息，请访问 Route 53 [documentation](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/AboutHZWorkingWith.html) 或在 Route 53 [Developer Guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/hosted-zones-migrating.html) 中查看迁移推荐。对于定价详情，请访问 Route 53 [pricing page](https://aws.amazon.com/route53/pricing/) 中的 Authoritative DNS 部分。

---

# AWS SAM 现已支持 Amazon API Gateway 自定义域名为私有 REST API

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/04/aws-sam-api-gateway-custom-domain-names/](https://aws.amazon.com/about-aws/whats-new/2025/04/aws-sam-api-gateway-custom-domain-names/)  

**发布时间:** 2025-04-08  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS SAM 现已支持 Amazon API Gateway 自定义域名为私有 REST API  

发表于：2025 年 4 月 8 日  

[AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) (AWS SAM) 现已支持 [Amazon API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html) 的私有 REST API 自定义域名 (Custom Domain Names) 功能。使用 SAM 构建无服务器应用程序的开发人员现在可以无缝地将私有 API 的自定义域名直接集成到他们的 SAM 模板中，从而无需使用其他工具单独配置自定义域名。  
  
Amazon API Gateway 允许您为私有 REST API 创建自定义域名 (Custom Domain Names)，例如 private.example.com，从而为 API 调用者提供更简单直观的 URL。通过私有自定义域名，您可以降低复杂性、使用 TLS 加密配置安全措施，以及管理与域名关联的 TLS 证书的生命周期。AWS SAM 是一组开源工具（例如 SAM、SAM CLI），它简化了您的开发生命周期中的编写、构建、部署、测试和监控阶段，从而轻松构建和管理无服务器应用程序。此次发布让您能够使用 SAM 和 [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli.html) 轻松配置私有 REST API 的自定义域名。  
  
要开始使用，请更新 SAM CLI 到最新版本，并在 SAM 模板中将 *AWS::Serverless::Api* 资源的 EndpointConfiguration 设置为 PRIVATE，并在 Domain 属性的 Policy 字段中指定策略文档。SAM 将自动生成 *DomainNameV2* 和 *BasePathMappingV2* 资源。要了解更多信息，请访问 [AWS SAM 文档](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-api.html)。您可以在 [API Gateway 博客文章](https://aws.amazon.com/blogs/compute/implementing-custom-domain-names-for-private-endpoints-with-amazon-api-gateway/) 中了解更多关于私有 REST API 自定义域名的内容。

---

---
# 负载均衡器容量单位预留 for 网关负载均衡器 (Gateway Load Balancer)

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/04/load-balancer-capacity-unit-reservation-gateway-load-balancers](https://aws.amazon.com/about-aws/whats-new/2025/04/load-balancer-capacity-unit-reservation-gateway-load-balancers)

**发布时间:** 2025-04-10

**厂商:** AWS

**类型:** 新增功能 (WHATSNEW)

---
# 负载均衡器容量单位预留 for 网关负载均衡器 (Gateway Load Balancer)

发布日期: 2025 年 4 月 10 日  

网关负载均衡器 (Gateway Load Balancer) 现已支持负载均衡器容量单位 (Load Balancer Capacity Unit) 预留功能，这让您可以主动设置负载均衡器的最小带宽容量，从而补充其现有的基于流量模式自动缩放 (auto-scale) 能力。  
  
网关负载均衡器 (Gateway Load Balancer) 有助于您部署、扩展和管理第三方虚拟设备。通过此功能，您可以为预期的流量激增预留保证容量。这种负载均衡器容量单位 (Load Balancer Capacity Unit) 预留特别适合于诸如将新工作负载引入到网关负载均衡器 (Gateway Load Balancer) 托管服务中的场景，而无需等待自然缩放，或者为防火墙应用维持最小带宽容量，以满足特定服务级别协议 (SLA) 或合规性要求。在使用此功能时，您只需为预留的负载均衡器容量单位 (Load Balancer Capacity Unit) 以及超出预留的任何额外使用付费。您可以通过弹性负载均衡 (ELB) 控制台或 API 轻松配置此功能。  
  
此功能适用于网关负载均衡器 (Gateway Load Balancer) 在以下 AWS 区域：美国东部 (北弗吉尼亚)、美国东部 (俄亥俄)、美国西部 (俄勒冈)、亚太地区 (香港)、亚太地区 (新加坡)、亚太地区 (悉尼)、亚太地区 (东京)、欧洲 (法兰克福)、欧洲 (爱尔兰) 和欧洲 (斯德哥尔摩)。此功能不支持网关负载均衡器端点 (Gateway Load Balancer Endpoint)。要了解更多信息，请参考 [GWLB 文档](https://docs.aws.amazon.com/elasticloadbalancing/latest/gateway/capacity-unit-reservation.html)。

---

# AWS 简化 Amazon VPC 对等连接 (VPC Peering) 计费

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-vpc-peering-billing/](https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-vpc-peering-billing/)  

**发布时间:** 2025-04-11  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS 简化 Amazon VPC 对等连接 (VPC Peering) 计费  

发布日期: 2025 年 4 月 11 日  

从今天起，我们通过在账单中引入一种新的使用类型，让客户更容易理解同一 AWS 区域 (AWS Region) 内不同可用区 (Availability Zone) 之间的 VPC 对等连接 (VPC Peering) 使用情况。这些变更不会影响客户的收费，而是帮助他们轻松掌握 VPC 对等连接 (VPC Peering) 成本，从而根据成本、性能和管理便利性选择合适的架构。  
  
VPC 对等连接 (VPC Peering) 是 Amazon VPC 的一个功能，允许客户在两个 VPC 之间建立网络连接，从而使用私有 IPv4 或 IPv6 地址路由流量。在此之前，VPC 对等连接 (VPC Peering) 使用情况被归入区域内数据传输使用量中，这让客户难以理解其使用和收费情况。通过此次发布，客户现在可以在 [Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/) 或 [Cost and Usage Report](https://aws.amazon.com/aws-cost-management/aws-cost-and-usage-reporting/) 中查看其 VPC 对等连接 (VPC Peering) 使用情况，使用新的使用类型“Region_Name-VpcPeering-In/Out-Bytes”。客户无需对现有 VPC 对等连接 (VPC Peering) 进行任何修改，这些变更将自动应用。  
  
VPC 对等连接 (VPC Peering) 连接上传输的数据定价保持不变。这些变更将适用于所有 AWS 商业区域和 AWS Gov Cloud (US) 区域。

---

---
# AWS Lambda@Edge 宣布高级日志控制

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/04/aws-lambda-edge-advanced-logging-controls/](https://aws.amazon.com/about-aws/whats-new/2025/04/aws-lambda-edge-advanced-logging-controls/)  

**发布时间:** 2025-04-14  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS Lambda@Edge 宣布高级日志控制  

发表于: 2025-04-14   

AWS Lambda@Edge 现在支持 [AWS Lambda 的高级日志控制 (advanced logging controls)](https://aws.amazon.com/blogs/compute/introducing-advanced-logging-controls-for-aws-lambda-functions/)，以改善函数日志在边缘位置的捕获、处理和消费方式。这一增强功能让您对日志数据有更多控制，便于监控应用行为并快速解决问题。  
  
新的 Lambda@Edge 高级日志控制为您提供了三种灵活的方式来管理和分析日志。新 JSON 结构化日志 (JSON structured logs) 让您更容易搜索、过滤和分析大量日志条目，而无需使用自定义日志库。日志级别粒度控制 (Log level granularity controls) 可以即时切换日志级别，让您在调查问题时过滤特定类型的日志，如错误或调试信息。自定义 CloudWatch 日志组选择 (Custom CloudWatch log group selection) 让您选择 Lambda@Edge 发送日志的 Amazon CloudWatch 日志组，从而更轻松地聚合和管理大规模日志。  
  
要开始使用，您可以使用 Lambda API、Lambda 控制台、AWS CLI、AWS Serverless Application Model (SAM) 和 AWS CloudFormation 为您的 Lambda 函数指定高级日志控制。要了解更多，请访问 [Lambda 开发者指南](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-cloudwatchlogs.html#monitoring-cloudwatchlogs-advanced) 和 [CloudFront 开发者指南](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/edge-functions-logs.html#lambda-at-edge-logs) 。

---

# Amazon CloudFront 宣布为 apex 域名 (apex domains) 提供 Anycast Static IPs 支持

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-cloudfront-anycast-static-ips-apex-domains](https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-cloudfront-anycast-static-ips-apex-domains)

**发布时间:** 2025-04-16

**厂商:** AWS

**类型:** WHATSNEW

---

# Amazon CloudFront 宣布为 apex 域名 (apex domains) 提供 Anycast Static IPs 支持

发布于：2025 年 4 月 16 日  

Amazon CloudFront 宣布为 apex 域名 (apex domains) 提供 Anycast Static IPs 支持，这让客户能够轻松地将他们的根域名 (如 example.com) 与 CloudFront 结合使用。这一新功能通过仅提供 3 个静态 IP 地址（而非之前的 21 个），简化了 DNS 管理 (DNS management)，从而更容易配置和管理 apex 域名与 CloudFront 分发 (distributions)。  
  
此前，客户需要创建 CNAME 记录 (CNAME records) 来指向 CloudFront。但是，由于 DNS 规则 (DNS rules)，根域名 (apex domains) 无法指向 CNAME 记录，只能使用 A 记录 (A records) 或 Route53 的 ALIAS 记录 (ALIAS records)。借助新的 Anycast Static IPs 支持，客户现在可以轻松为他们的 apex 域名 配置 A 记录。组织机构可以保留现有的 DNS 基础设施，同时利用 CloudFront 的全球内容分发网络 (content delivery network) 来交付 apex 域名，实现低延迟和高数据传输速度。Anycast 路由 (Anycast routing) 会自动将流量导向最佳的边缘位置 (edge location)，确保全球终端用户获得高性能内容交付。  
  
CloudFront 从所有 CloudFront 边缘位置 (edge locations) 支持 Anycast Static IPs。这不包括由 Sinnet 运营的 Amazon Web Services China (Beijing) 区域，以及由 NWCD 运营的 Amazon Web Services China (Ningxia) 区域。标准 CloudFront 定价 (pricing) 适用，并针对 Anycast Static IP 地址收取额外费用。如需了解更多，请访问 [CloudFront 开发者指南](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/request-static-ips.html) 以获取详细文档和实施指导。

---

# Amazon VPC Reachability Analyzer 和 Amazon VPC Network Access Analyzer 现已在欧洲 (Spain) 区域可用

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-vpc-reachability-network-access-analyzer-spain/](https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-vpc-reachability-network-access-analyzer-spain/)

**发布时间:** 2025-04-24

**厂商:** AWS

**类型:** WHATSNEW

---

# Amazon VPC Reachability Analyzer 和 Amazon VPC Network Access Analyzer 现已在欧洲 (Spain) 区域可用

发布日期: 2025 年 4 月 24 日  

随着此次发布，VPC Reachability Analyzer (VPC Reachability Analyzer) 和 VPC Network Access Analyzer (VPC Network Access Analyzer) 现已在欧洲 (Spain) 区域可用。  
  
VPC Reachability Analyzer 允许您通过分析虚拟私有云 (VPC) 中的网络配置，诊断源资源和目标资源之间的网络可达性。例如，Reachability Analyzer 可以帮助您识别 VPC 路由表中缺少的路由表条目，从而解决 Account A 中的 EC2 实例无法连接到 AWS Organization 中 Account B 中的另一个 EC2 实例的问题。  
  
VPC Network Access Analyzer 允许您识别 AWS 资源上意外的网络访问。使用 Network Access Analyzer，您可以验证 VPC 资源的网络访问是否符合您的安全和合规性指南。例如，您可以创建一个范围来验证财务团队使用的 VPC 是否与开发团队使用的 VPC 完全分离、独立且不可达。  
  
有关更多功能信息，请访问 [VPC Reachability Analyzer](https://docs.aws.amazon.com/vpc/latest/reachability/what-is-reachability-analyzer.html) 和 [VPC Network Access Analyzer](https://docs.aws.amazon.com/vpc/latest/network-access-analyzer/what-is-network-access-analyzer.html) 的文档。有关定价详情，请参考 [Amazon VPC 定价页面](https://aws.amazon.com/vpc/pricing/) 中的 Network Analysis 选项卡。

---

# Amazon Route 53 Profiles 现已支持 VPC 端点

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-route-53-profiles-vpc-endpoints](https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-route-53-profiles-vpc-endpoints)

**发布时间:** 2025-04-28

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon Route 53 Profiles 现已支持 VPC 端点

发表于: 2025 年 4 月 28 日 

今天，AWS 宣布 Amazon Route 53 Profiles 支持 VPC 端点 (VPC Endpoints)，允许您为接口 VPC 端点 (Interface VPC Endpoints) 创建、管理和共享私有托管区域 (Private Hosted Zones，简称 PHZs)，并将其跨多个 VPC 和 AWS 账户在组织内共享。这一增强功能简化了 VPC 端点的管理过程，通过流畅地创建和关联接口 VPC 端点管理的 PHZs 与 VPC 和 AWS 账户，而无需手动关联它们。  

Route 53 Profiles 让您轻松为 VPC 相关的 DNS 设置创建一或多个配置，例如私有托管区域和 Route 53 Resolver 规则 (Route 53 Resolver Rules)，并在多个 VPC 和 AWS 账户之间共享。新功能帮助您集中管理与接口 VPC 端点相关的 PHZs，减少了管理开销，并降低了配置错误的风险。这一特性消除了为 VPC 端点与单个 VPC 和账户创建和手动关联 PHZs 的需求，从而为网络管理员节省了时间和精力。此外，它通过提供一种集中式方法来管理组织的 AWS 基础设施中 VPC 端点的 DNS 解析，提高了安全性和一致性。  

Route 53 Profiles 对 VPC 端点的支持现已在 [此处](https://docs.aws.amazon.com/general/latest/gr/r53.html) 提到的 AWS 区域中可用。要了解更多关于此功能及其对您组织的好处，请访问 Amazon Route 53 [文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/profiles.html)。您可以通过 AWS 管理控制台中的 Amazon Route 53 控制台或 AWS CLI 开始使用。要了解 Route 53 Profiles 的定价，请参见 [此处](https://aws.amazon.com/route53/pricing/)。

---

# 发布 Amazon CloudFront 的 SaaS Manager

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/04/saas-manager-amazon-cloudfront/](https://aws.amazon.com/about-aws/whats-new/2025/04/saas-manager-amazon-cloudfront/)  

**发布时间:** 2025-04-28  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# 发布 Amazon CloudFront 的 SaaS Manager  

发表于: 2025 年 4 月 28 日  

今天，AWS 发布 CloudFront SaaS Manager (CloudFront SaaS Manager)，这是一个新的 Amazon CloudFront 功能，旨在帮助软件即服务 (SaaS) 提供商、网络开发平台以及拥有多个品牌/网站的公司的用户高效管理多网站的内容分发。CloudFront SaaS Manager 提供统一的体验，减轻了在规模化管理多个网站时的操作负担，包括 TLS 证书管理、DDoS 保护以及可观测性。  
  
CloudFront SaaS Manager 引入了可重用配置设置，消除了冗余配置，让用户能够在网站间保持一致的设置。这不仅节省了时间，还降低了配置错误的潜在风险。通过 CloudFront SaaS Manager，用户能受益于最佳的 CDN 和安全默认设置，确保高性能和安全保护，遵循 AWS 最佳实践。此外，CloudFront SaaS Manager 可以通过简化的 AWS Certificate Manager (ACM) 集成自动处理 TLS 证书的请求、颁发和关联，从而应对公司客户基数扩展时面临的证书管理、安全策略执行以及跨账户同步的复杂性。  
  
获取更多关于使用 CloudFront SaaS Manager 的信息，请查看[这里](https://aws.amazon.com/blogs/aws/reduce-your-operational-overhead-today-with-amazon-cloudfront-saas-manager/)，在 Amazon [CloudFront SaaS Manager 页面](https://aws.amazon.com/cloudfront/features/saas-manager/) 以及 [Amazon CloudFront 开发者指南](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-config-options.html)。

---

# 使用 Amazon CloudFront 的自动化 HTTP 验证公共证书

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/04/automated-http-validated-public-certificates-amazon-cloudfront](https://aws.amazon.com/about-aws/whats-new/2025/04/automated-http-validated-public-certificates-amazon-cloudfront)  

**发布时间:** 2025-04-28  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# 使用 Amazon CloudFront 的自动化 HTTP 验证公共证书  

发布日期: 2025 年 4 月 28 日  

AWS 证书管理器 (ACM) 宣布为 [Amazon CloudFront](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-https.html) 提供自动化公共 TLS 证书。CloudFront 用户现在只需在创建新的 CloudFront 内容交付应用时勾选一个选项，即可获得所需的公共证书，以启用 TLS。ACM 和 CloudFront 会共同自动请求、颁发并将所需的公共证书与 CloudFront 关联。只要证书在使用中，并且证书域的流量路由到 CloudFront，ACM 还会自动续期这些证书。在此之前，要设置类似的安全 CloudFront 分发，用户必须通过 ACM 请求公共证书、验证域，然后将颁发的证书与 CloudFront 分发关联。这种选项仍可供用户使用。  
  
ACM 使用一种常见的域验证方法，即 HTTP (HTTP) 验证或基于文件的验证，来颁发和续期这些证书。域验证确保 ACM 只向授权获取域证书的域用户颁发证书。网络和证书管理员仍然可以使用 ACM 查看和监控这些证书。虽然 ACM 自动管理证书生命周期，但管理员可以使用 ACM 的 [证书生命周期 CloudWatch 事件](https://docs.aws.amazon.com/acm/latest/userguide/cloudwatch-events.html) 来监控证书更新，并将信息发布到集中的安全信息和事件管理 (SIEM) 和/或企业资源规划 (ERP) 解决方案。  
  
要了解此功能的更多信息，请参阅我们的 [文档](https://docs.aws.amazon.com/acm/latest/userguide/http-validation.html)。您可以在这里了解更多关于 ACM [的信息](https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html) ，以及 CloudFront [的信息](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-config-options.html)。

---

# AWS Client VPN 现已支持客户端路由强制执行 (Client Routes Enforcement)

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/04/aws-client-vpn-client-routes-enforcement/](https://aws.amazon.com/about-aws/whats-new/2025/04/aws-client-vpn-client-routes-enforcement/)  

**发布时间:** 2025-04-28  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS Client VPN 现已支持客户端路由强制执行 (Client Routes Enforcement)  

发布日期: 2025 年 4 月 28 日  

今天，AWS 宣布了一个新的 AWS Client VPN 功能，该功能监控设备网络路由、防止 VPN 流量泄漏，并加强远程访问安全。此功能持续跟踪用户设备的路由表，确保出站流量按照您配置的设置通过 VPN 隧道 (VPN tunnel) 流动。如果检测到任何修改的网络路由设置，它会自动将路由恢复到原始配置。  

AWS Client VPN 允许管理员在用户设备上配置路由，以将流量路由通过 VPN。例如，管理员可能配置终端用户设备使用 VPN 连接访问 10.0.0.0/24 网络，而其他流量从设备本地直接发出。然而，连接设备可能偏离组织的配置，导致 VPN 泄漏。例如，即使您配置了 10.0.0.0/24 网络的流量通过 VPN，用户或其他在设备上运行的客户端仍可能修改设置并绕过 VPN。对于此功能启用后，我们的 VPN 客户端会持续监控路由，并通过修复路由回原始配置来自动纠正偏差。此功能确保管理员的配置始终应用于终端用户，维护组织的连接完整性。  

此功能在所有 AWS Client VPN 全面可用 (generally available) 的区域提供，且无需额外费用。  

要了解更多关于 Client VPN 的信息：  

- 访问 AWS Client VPN [产品页面](https://aws.amazon.com/vpn/)  
- 阅读 AWS Client VPN 客户端路由强制执行 [文档](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-working-cre.html)

---

# Amazon VPC Lattice 现已支持 IPv6 用于管理端点

**原始链接：** [https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-vpc-lattice-ipv6-management-endpoints/](https://aws.amazon.com/about-aws/whats-new/2025/04/amazon-vpc-lattice-ipv6-management-endpoints/)  

**发布时间：** 2025-04-30  

**厂商：** AWS  

**类型：** WHATSNEW  

---  
# Amazon VPC Lattice 现已支持 IPv6 用于管理端点  

发表于：2025 年 4 月 30 日  

Amazon VPC Lattice 引入了双栈支持，用于管理 API，让您可以使用 Internet Protocol Version 6 (IPv6)、Internet Protocol Version 4 (IPv4) 或双栈客户端进行连接。双栈支持也适用于从您的 Amazon Virtual Private Cloud (VPC) 通过 [AWS PrivateLink](https://docs.aws.amazon.com/vpc-lattice/latest/ug/vpc-interface-endpoints.html) 私密访问 Amazon VPC Lattice 管理 API 端点时。新双栈端点将通过一个新的 AWS DNS 域名提供。原有 Amazon VPC Lattice 管理 API 端点将继续保留，以确保向后兼容。  
  
Amazon VPC Lattice 是一个应用网络服务，能够简化服务间通信的连接、安全和监控。您可以使用 Amazon VPC Lattice 实现跨账号和跨 VPC 连接，以及为您的负载提供应用层负载均衡。不管底层计算类型是实例、容器还是无服务器，开发人员都可以选择其偏好的计算平台进行原生集成。通过 VPC Lattice 端点同时支持 IPv4 和 IPv6 客户端，您可以逐步从 IPv4 过渡到基于 IPv6 的系统和应用，而无需一次性全部切换。这有助于满足 IPv6 合规要求，并消除使用昂贵网络设备进行 IPv4 和 IPv6 地址转换的需要。  

要了解更多信息，请参阅 VPC Lattice [用户指南](https://docs.aws.amazon.com/vpc-lattice/latest/ug/what-is-vpc-lattice.html#service-endpoints-specify-endpoints) 和 [IPv6 on AWS](https://docs.aws.amazon.com/whitepapers/latest/ipv6-on-aws/internet-protocol-version-6.html)。

---

# Amazon Route 53 Resolver DNS Firewall 在更多区域可用

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-route-53-resolver-dns-firewall-additional-regions/](https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-route-53-resolver-dns-firewall-additional-regions/)  

**发布时间:** 2025-05-01  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon Route 53 Resolver DNS Firewall 在更多区域可用  

发布日期: 2025 年 5 月 1 日  

从今天起，您可以在亚太地区 (Thailand) 和墨西哥 (Central) 区域，使用 Amazon Route 53 Resolver DNS Firewall (Amazon Route 53 Resolver DNS Firewall) 和 DNS Firewall Advanced (DNS Firewall Advanced)，来管理和过滤您 Amazon Virtual Private Cloud (VPC) 的出站 DNS 流量。  

Amazon Route 53 Resolver DNS Firewall 是一个托管服务，可帮助您阻止针对声誉较低或可疑恶意域的 DNS 查询，并允许针对可信域的查询。此外，DNS Firewall Advanced 是 DNS Firewall 的一个功能，可检测并阻止与 Domain Generation Algorithms (DGA) 和 DNS Tunneling 威胁相关的 DNS 流量。Amazon Route 53 Resolver DNS Firewall 仅可为 Route 53 Resolver 启用，而 Route 53 Resolver 是一个递归 DNS 服务器，默认在所有 Amazon Virtual Private Cloud (VPC) 中可用。它会响应 VPC 内 AWS 资源针对公共 DNS 记录、VPC 特定域名以及 Route 53 私有托管区域的 DNS 查询。  

请查看 [此处](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall-availability.html) 以获取 Amazon Route 53 Resolver DNS Firewall 可用 AWS 区域的列表。访问我们的 [产品页面](https://aws.amazon.com/route53/resolver-dns-firewall/) 和 [文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall.html) ，以了解更多关于 Amazon Route 53 Resolver DNS Firewall 及其定价的信息。

---

# Amazon VPC IPAM 现已支持将成本分配到 AWS Organization 成员账户

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-vpc-ipam-cost-distribution-aws-organization-member-accounts](https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-vpc-ipam-cost-distribution-aws-organization-member-accounts)  

**发布时间:** 2025-05-01  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon VPC IPAM 现已支持将成本分配到 AWS Organization 成员账户  

发布于: 2025 年 5 月 1 日   

今日，AWS 宣布 Amazon VPC IP Address Manager (IPAM) 现已支持将 IPAM 成本分配到 AWS Organizations 成员账户。这让您能轻松地将成本分配给内部团队，用于他们的 IPAM 使用。  

VPC IPAM 可以简化您对 AWS 工作负载 IP 地址的规划、跟踪和监控。当您为 AWS Organization 启用 IPAM 时，IPAM 会聚合整个组织的 IP 地址使用情况，并向创建 IPAM 的 AWS 账户收费。通过此新功能，您可以将费用直接分配到 AWS Organizations 成员账户，针对它们的单独使用。例如，您可能在中央 AWS 账户中启用了 IPAM，该账户运行多个网络服务，并希望将 IPAM 费用分配给内部团队，现在您可以使用此功能轻松实现。  

此功能现已在所有支持 Amazon VPC IPAM 的 AWS 区域 (AWS Regions) 中可用，包括 AWS 中国区域和 AWS GovCloud (US) 区域。  

要了解更多关于 IPAM 的信息，请查看 [IPAM 文档](https://docs.aws.amazon.com/vpc/latest/ipam/what-it-is-ipam.html)。关于定价详情，请参考 [Amazon VPC 定价页面](https://aws.amazon.com/vpc/pricing/) 中的 IPAM 选项卡。

---

# Amazon Connect Contact Lens 实时仪表板 (Real-time dashboards) 现已在 AWS GovCloud (US-West) 可用

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-connect-contact-lens-real-time-dashboards-aws-govcloud-us-west](https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-connect-contact-lens-real-time-dashboards-aws-govcloud-us-west)

**发布时间:** 2025-05-05

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon Connect Contact Lens 实时仪表板 (Real-time dashboards) 现已在 AWS GovCloud (US-West) 可用

发表于: 2025 年 5 月 5 日 

Amazon Connect Contact Lens 的实时队列和代理性能仪表板 (Real-time queue and agent performance dashboards)，以及流程性能仪表板 (Flows performance dashboards) 现已在 AWS GovCloud (US-West) 上可用，这是一个为政府和公共部门客户设计的安全云环境。新仪表板 (dashboards) 让您能够监控代理的实时活动，并快速采取行动，例如从单一界面中点击几下即可监听通话、介入 (barge) 通话，或更改代理状态。这些仪表板 (dashboards) 现在允许您定义小部件级别的过滤器和分组、重新排序和调整列大小，以及删除或添加新指标。通过这些仪表板，您可以查看和比较实时和历史聚合性能、趋势以及洞见，使用自定义定义的时间段（如周与周比较）、摘要图表、时间序列图表等。例如，如果代理处于错误状态，您可以自动用红色突出显示，从而快速视觉指示代理可能需要额外帮助来将状态变回可用。

Amazon Connect Contact Lens 的仪表板 (dashboards) 在所有提供 Amazon Connect 的 AWS 商业区域 (Regions) 和 AWS GovCloud (US) 区域中可用。要了解更多关于仪表板的信息，请参阅 [Amazon Connect 管理员指南](https://docs.aws.amazon.com/connect/latest/adminguide/dashboards.html)。要了解更多关于 Amazon Connect（AWS 基于云的联系中心）的细节，请访问 [Amazon Connect 网站](https://aws.amazon.com/connect/)。

---

# Amazon Route 53 Resolver 查询日志记录 (Route 53 Resolver Query Logging) 现已在两个新 AWS 区域可用

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-route-53-resolver-query-logging-new-aws-regions](https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-route-53-resolver-query-logging-new-aws-regions)

**发布时间:** 2025-05-07

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon Route 53 Resolver 查询日志记录 (Route 53 Resolver Query Logging) 现已在两个新 AWS 区域可用

发布于：2025 年 5 月 7 日

今天，我们宣布 Route 53 Resolver 查询日志记录 (Route 53 Resolver Query Logging) 在亚太地区 (Thailand) 和 墨西哥 (Central) 区域可用，这让您能够记录源自您的 Amazon Virtual Private Cloud (Amazon VPC) 中的 DNS 查询。一旦启用查询日志记录，您可以查看哪些域名已被查询、查询源的 AWS 资源（包括源 IP 和实例 ID）以及收到的响应。

Route 53 Resolver 是默认在所有 Amazon VPC 中可用的 Amazon DNS 服务器。Route 53 Resolver 会响应来自 VPC 内 AWS 资源的 DNS 查询，这些查询针对公共 DNS 记录、Amazon VPC 特定 DNS 名称以及 Amazon Route 53 私有托管区域。通过 Route 53 Resolver 查询日志记录 (Route 53 Resolver Query Logging)，客户可以记录源自其 VPC 中的 DNS 查询和响应，无论这些查询是由 Route 53 Resolver 本地回答的，还是通过公共互联网解析的，或者是通过 [Resolver 端点 (Resolver Endpoints)](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html) 转发到本地 DNS 服务器。

您可以使用 [AWS 资源访问管理器 (RAM)](https://aws.amazon.com/ram/) 在多个账户间共享您的查询日志记录配置。您还可以选择将查询日志发送到 Amazon S3、Amazon CloudWatch Logs 或 Amazon Kinesis Data Firehose。

使用 Route 53 Resolver 查询日志记录 (Route 53 Resolver Query Logging) 无需额外费用，但您可能会因使用 Amazon S3、Amazon CloudWatch 或 Amazon Kinesis Data Firehose 而产生使用费用。要了解更多关于 Route 53 Resolver 查询日志记录 (Route 53 Resolver Query Logging) 的信息或开始使用，请访问 [Route 53 产品页面](https://aws.amazon.com/route53/resolver/) 或 [Route 53 文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-query-logs.html)。

---

# AWS 宣布在澳大利亚布里斯班开设新的 AWS Direct Connect 位置

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/05/aws-direct-connect-location-brisbane-australia](https://aws.amazon.com/about-aws/whats-new/2025/05/aws-direct-connect-location-brisbane-australia)  

**发布时间:** 2025-05-08  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS 宣布在澳大利亚布里斯班开设新的 AWS Direct Connect 位置  

发布时间: 2025 年 5 月 8 日  

今天，AWS 宣布在澳大利亚布里斯班附近的 NEXTDC B2 数据中心开设一个新的 [AWS Direct Connect](https://aws.amazon.com/directconnect) 位置。通过在新的位置将您的网络连接到 AWS，您可以获得对所有公共 AWS 区域（除中国区域外）、AWS GovCloud 区域以及 [AWS 本地扩展区域 (AWS Local Zones)](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) 的私有直接访问。该位置是布里斯班的首个 AWS Direct Connect 位置，也是澳大利亚的第八个 AWS Direct Connect 位置。此 Direct Connect 位置提供专用的 10 Gbps 和 100 Gbps 连接，并支持 MACsec 加密。  
  
AWS Direct Connect 服务让您能够在 AWS 与您的数据中心、办公室或联合托管环境之间建立私有的物理网络连接。这些私有连接可提供比通过公共互联网连接更稳定的网络体验。  
  
有关全球超过 148 个 Direct Connect 位置的更多信息，请访问 Direct Connect [位置](https://aws.amazon.com/directconnect/locations/) 部分，或查看 [产品详情页面](https://aws.amazon.com/directconnect)。或者，访问我们的 [入门页面](https://aws.amazon.com/directconnect/getting-started/)，了解如何购买和部署 Direct Connect。

---

# Amazon VPC Reachability Analyzer 现支持资源排除

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-vpc-reachability-analyzer-resource-exclusion](https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-vpc-reachability-analyzer-resource-exclusion)  

**发布时间:** 2025-05-09  

**厂商:** AWS  

**类型:** 新增功能  

---  
# Amazon VPC Reachability Analyzer 现支持资源排除  

发表于: 2025 年 5 月 9 日  

Amazon [VPC 可达性分析器 (VPC Reachability Analyzer)](https://docs.aws.amazon.com/vpc/latest/reachability/what-is-reachability-analyzer.html) 现支持在分析源和目标之间的可达性时排除网络资源，这为您提供了更大的灵活性来运行可达性分析。  
  
VPC 可达性分析器是一种配置分析功能，可帮助您检查在虚拟私有云 (virtual private clouds, VPCs) 中源资源和目标资源之间的网络可达性。通过此功能，您可以轻松识别网络中的备用流量路径。例如，如果您想找到从互联网网关 (Internet Gateway) 到弹性网络接口 (Elastic Network Interfaces, ENIs) 的任何路径，而该路径不经过网络防火墙 (Network Firewall) 进行检查，您可以指定 Network Firewall 作为资源排除项，然后运行可达性分析。如果分析结果显示存在可达路径，则表示您的网络中存在备用路径，您可以采取必要的行动。  
  
要了解更多关于 Amazon VPC Reachability Analyzer 的信息，请访问 [文档](https://docs.aws.amazon.com/vpc/latest/reachability/what-is-reachability-analyzer.html)。要查看 Reachability Analyzer 的定价，请访问 [Amazon VPC 定价](https://aws.amazon.com/vpc/pricing/)。

---

# AWS EC2 实例现支持 ENA 队列分配功能，用于您的网络接口

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/05/aws-ec2-instances-ena-queue-allocation-network-interfaces/](https://aws.amazon.com/about-aws/whats-new/2025/05/aws-ec2-instances-ena-queue-allocation-network-interfaces/)

**发布时间:** 2025-05-12

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS EC2 实例现支持 ENA 队列分配功能，用于您的网络接口

发布日期：2025 年 5 月 12 日  

AWS 宣布为 Elastic Network Adapter (ENA) 推出一个新功能，该功能允许在 EC2 实例上为每个弹性网络接口 (ENI) 灵活分配队列。ENA 队列作为 ENI 的关键组件，通过在可用队列间负载均衡发送和接收的数据，来高效管理网络流量。此网络接口功能通过灵活分配多个发送和接收 ENA 队列，将数据包处理任务高效分布到虚拟 CPU (vCPUs) 上，从而优化网络性能。用户现在可以对网络资源和实例性能进行细粒度控制，从而根据特定工作负载需求调整 ENA 队列分配。  

在此公告之前，用户可以为实例配置额外的 ENI，但 ENA 队列是静态分配给每个 ENI，且无法灵活调整。现在，用户可以从实例的总队列池中动态分配 ENA 队列到各个 ENI，总可用队列数量会根据实例类型和大小而异。这种灵活的 ENA 队列分配通过优化资源分布，实现最大化虚拟 CPU (vCPUs) 利用率。网络密集型应用程序可以分配更多队列，而 CPU 密集型应用程序则可以使用较少的队列。  

EC2 弹性队列 (EC2 Flexible Queues) 在所有 AWS 商业区域均可用。要了解更多信息以及支持的实例类型，请查看最新的 [EC2 Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ena-nitro-perf.html) 。

---

# AWS 宣布在土耳其伊斯坦布尔的新 AWS Direct Connect 位置

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/05/aws-direct-connect-location-istanbul-turkey/](https://aws.amazon.com/about-aws/whats-new/2025/05/aws-direct-connect-location-istanbul-turkey/)  

**发布时间:** 2025-05-12  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS 宣布在土耳其伊斯坦布尔的新 AWS Direct Connect 位置  

发表于: 2025 年 5 月 12 日  

今天，AWS 宣布在土耳其伊斯坦布尔附近的 Equinix IL4 数据中心开设一个新的 AWS Direct Connect (AWS Direct Connect) 位置。通过在该新位置将您的网络连接到 AWS，您可以获得对所有公共 AWS 区域 (除中国区域外)、AWS GovCloud 区域以及 [AWS 本地扩展区域 (Local Zones)](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) 的私有直接访问。这是一个土耳其的首个 AWS Direct Connect 位置。该位置提供专用的 10 Gbps 和 100 Gbps 连接，并支持 MACsec 加密 (MACsec encryption)。  
  
AWS Direct Connect 服务使您能够在 AWS 和您的数据中心、办公室或联合托管环境之间建立私有的物理网络连接。这些私有连接可提供比通过公共互联网连接更稳定的网络体验。  
  
有关全球超过 149 个 Direct Connect 位置的更多信息，请访问 Direct Connect [位置](https://aws.amazon.com/directconnect/locations/) 部分或 [产品详情页面](https://aws.amazon.com/directconnect/)。或者，访问我们的 [入门页面](https://aws.amazon.com/directconnect/getting-started/)，了解如何购买和部署 Direct Connect。

---

# Amazon VPC 为默认创建的 VPC 资源添加 CloudTrail 日志记录

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-vpc-cloudtrail-logging-resources-default/](https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-vpc-cloudtrail-logging-resources-default/)  

**发布时间:** 2025-05-13  

**厂商:** AWS  

**类型:** WHATSNEW  

---  

# Amazon VPC 为默认创建的 VPC 资源添加 CloudTrail 日志记录  

发布日期: 2025 年 5 月 13 日  

Amazon VPC 已增强 CloudTrail (AWS CloudTrail) 日志记录功能，以包含在创建 VPC 时默认创建的 VPC 资源 (VPC resources)。这一增强功能提供了更好的 VPC 资源可见性，有助于审计和治理工作。  

在此之前，CloudTrail 日志记录仅包括客户显式创建的资源。客户需要手动整理环境中的默认资源列表，以满足审计要求。现在，通过此功能，客户可以查看在创建或删除 VPC 时触发的默认资源事件，例如安全组 (Security Group)、网络访问控制列表 (Network ACL) 和路由表 (Route Table) 的创建或删除。这些事件会在 AWS 管理控制台 (AWS Management Console) 中的 CloudTrail 中记录。  
  
默认 VPC 资源的 CloudTrail 日志记录已在所有 AWS 商用区域和 AWS GovCloud (US) 区域 (AWS GovCloud (US) Regions) 可用，且无需额外费用。要了解更多此功能信息，请参考我们的[文档](https://docs.aws.amazon.com/vpc/latest/userguide/monitoring.html)。

---

# AWS 宣布在旧金山湾区开设新的 AWS 数据传输终端 (AWS Data Transfer Terminal) 位置

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/05/aws-data-transfer-terminal-san-francisco-bay-area/](https://aws.amazon.com/about-aws/whats-new/2025/05/aws-data-transfer-terminal-san-francisco-bay-area/)

**发布时间:** 2025-05-13

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS 宣布在旧金山湾区开设新的 AWS 数据传输终端 (AWS Data Transfer Terminal) 位置

发布日期: 2025 年 5 月 13 日  

今天，AWS 宣布在加利福尼亚州圣克拉拉的 CoreSite SV8 内开设新的 AWS 数据传输终端 (AWS Data Transfer Terminal) 位置，这将是加利福尼亚州的第二个位置，加入现有的洛杉矶和纽约市位置。AWS 数据传输终端 (AWS Data Transfer Terminal) 是一个安全的物理场所，您可以将存储设备带入并通过高吞吐量网络连接上传数据到 AWS，包括 Amazon Simple Storage Service (Amazon S3)、Amazon Elastic File System (Amazon EFS) 等服务。  
  
AWS 数据传输终端 (AWS Data Transfer Terminal) 非常适合需要快速、安全地将大量数据传输到 AWS 的客户。常见用例涵盖多个行业和应用场景，包括媒体和娱乐行业的视频制作数据处理、汽车行业的先进驾驶员辅助系统 (Advanced Driver Assistance Systems, ADAS) 培训数据、金融服务行业的遗留数据迁移，以及工业和农业部门的设备传感器数据上传。一旦上传，您就可以立即利用 AWS 服务，例如使用 Amazon Athena 进行分析、使用 Amazon SageMaker 进行机器学习，或使用 Amazon Elastic Compute Cloud (Amazon EC2) 进行应用开发，从而将数据处理时间从几周缩短到几分钟。  
  
要了解更多信息，请访问数据传输终端 (AWS Data Transfer Terminal) [产品页面](https://aws.amazon.com/data-transfer-terminal/) 和 [文档](https://docs.aws.amazon.com/datatransferterminal/latest/userguide/what-is-dtt.html)。要开始使用，请在 [AWS Console](https://console.aws.amazon.com/datatransferterminal) 中为附近的 AWS 数据传输终端 (AWS Data Transfer Terminal) 预订位置。

---

# AWS Site-to-Site VPN Tunnel Endpoint Lifecycle Control 现已在 AWS Europe (Milan) 区域可用

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/05/aws-site-to-site-vpn-tunnel-endpoint-lifecycle-control-europe-milan-region](https://aws.amazon.com/about-aws/whats-new/2025/05/aws-site-to-site-vpn-tunnel-endpoint-lifecycle-control-europe-milan-region)  

**发布时间:** 2025-05-20  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS Site-to-Site VPN Tunnel Endpoint Lifecycle Control 现已在 AWS Europe (Milan) 区域可用  

发布于: 2025 年 5 月 20 日  

AWS Site-to-Site VPN Tunnel Endpoint Lifecycle Control 现已在 AWS Europe (Milan) 区域可用，提供更好的可见性和对 VPN 隧道维护更新的控制。  

AWS Site-to-Site VPN 是一个完全托管的服务 (AWS Site-to-Site VPN)，允许您使用 IP Security (IPSec) 隧道在数据中心或分支机构与 AWS 资源之间建立安全连接。启用 Tunnel Endpoint Lifecycle Control 功能后，您将提前获知即将到来的维护更新，以帮助您规划并最小化 VPN 连接的服务中断。它为您提供了额外的灵活性，在最适合您业务的时间应用 VPN 隧道端点的更新。  

要了解更多，请访问 [文档](https://docs.aws.amazon.com/vpn/latest/s2svpn/tunnel-endpoint-lifecycle.html)。

---

# AWS 宣布为 EC2 Public DNS 名称 添加 IPv6 支持

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/05/ipv6-support-ec2-public-dns-names/](https://aws.amazon.com/about-aws/whats-new/2025/05/ipv6-support-ec2-public-dns-names/)  

**发布时间:** 2025-05-22  

**厂商:** AWS  

**类型:** 最新动态  

---  
# AWS 宣布为 EC2 Public DNS 名称 添加 IPv6 支持  

发表于: 2025 年 5 月 22 日  

EC2 Public DNS 名称 (EC2 Public DNS names) 现在可以解析为与您的 EC2 实例和弹性网络接口 (Elastic Network Interfaces, ENI) 关联的 IPv6 全球单播地址 (IPv6 Global Unicast Address, AAAA 记录)。这让客户能够使用 EC2 Public DNS 名称，通过 IPv6 公开访问其启用了 IPv6 的 Amazon EC2 实例。  

在此之前，EC2 Public DNS 名称 会解析为实例的主 ENI 关联的公共 IPv4 地址 (A 记录)。因此，采用 IPv6 的客户需要使用特定的 IPv6 地址来访问仅 IPv6 的 Amazon EC2 实例，或者通过创建托管区域使用 Amazon Route 53 来使用自定义域名。EC2 Public DNS 名称 的 IPv6 支持让客户能够轻松访问其仅 IPv6 的 Amazon EC2 实例，或制定迁移计划，以便通过 IPv6 访问双栈实例，并通过简单的 DNS 切换实现。  

此功能适用于所有 AWS 商业区域和 AWS GovCloud (US) 区域，客户可以使用与启用 IPv4-only EC2 Public DNS 名称 相同的 VPC 设置来设置 IPv6 支持。要了解更多关于 EC2 Public DNS 名称 的 IPv6 支持信息，请参考我们的 [文档](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-naming.html) 。

---

# Amazon Route 53 Profiles 现已在三个额外 AWS 区域可用

**原始链接：** [https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-route-53-profiles-three-additional-regions/](https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-route-53-profiles-three-additional-regions/)  

**发布时间：** 2025-05-23  

**厂商：** AWS  

**类型：** WHATSNEW  

---  
# Amazon Route 53 Profiles 现已在三个额外 AWS 区域可用  

发表于：2025 年 5 月 23 日  

从今天起，Route 53 Profiles (Route 53 Profiles) 在亚太地区 (Thailand)、墨西哥 (Central) 和亚太地区 (Malaysia) 区域可用。  

Route 53 Profiles 允许您定义一个标准 DNS 配置 (Profile)，其中可能包括 Route 53 私有托管区域 (Private Hosted Zone) 关联、Route 53 Resolver 规则，以及 Route 53 Resolver DNS 防火墙规则组，并将此配置应用于您账户中的多个虚拟私有云 (VPC)。Route 53 Profiles 还可以用于强制执行 VPC 的 DNS 设置，包括 DNSSEC 验证、Resolver 反向 DNS 查询，以及 DNS 防火墙故障模式。您可以使用 AWS 资源访问管理器 (AWS Resource Access Manager) 将 Profiles 与组织中的其他 AWS 账户共享。Route 53 Profiles 通过单一配置简化了在区域内跨多个 VPC 和 AWS 账户的 Route 53 资源关联和 VPC 级 DNS 设置的管理，从而降低了管理每个资源关联和设置的复杂性。  

Route 53 Profiles 可在 [此处](https://docs.aws.amazon.com/general/latest/gr/r53.html) 提到的 AWS 区域中使用。要开始使用此功能，请访问 Route 53 [文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/profiles.html)。要了解更多定价信息，您可以访问 [Route 53 定价页面](https://aws.amazon.com/route53/pricing/) 。

---

# AWS Network Firewall 新增对多个 VPC 端点 的支持

**原始链接：** [https://aws.amazon.com/about-aws/whats-new/2025/05/aws-network-firewall-multiple-vpc-endpoints/](https://aws.amazon.com/about-aws/whats-new/2025/05/aws-network-firewall-multiple-vpc-endpoints/)  

**发布时间：** 2025-05-28  

**厂商：** AWS  

**类型：** WHATSNEW  

---  
# AWS Network Firewall 新增对多个 VPC 端点 的支持  

发表于：2025 年 5 月 28 日  

AWS Network Firewall 现已支持为单个防火墙配置多个 VPC 端点 (VPC endpoints) 。这项新功能为您提供了更多选项，可将 Network Firewall 部署扩展到多个 Amazon Virtual Private Cloud (VPC) 跨域，使用集中的安全策略。  
  
AWS Network Firewall 是一种托管的、云原生防火墙服务，可轻松为所有 Amazon VPC 部署基本的网络保护。Network Firewall 实例部署在 VPC 子网中，通过 VPC 端点 提供安全的连接。现在，您可以将每个可用区 (Availability Zone) 与防火墙关联多达 50 个 VPC 端点，并将流量路由通过防火墙进行检查，从而降低操作复杂性和成本，同时保护更多 VPC。  
  
多个 VPC 端点 功能在所有当前支持 AWS Network Firewall 的 [AWS 区域](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 中可用，包括 AWS GovCloud (US) 区域和中国区域。  
  
您可以通过 [Amazon VPC 控制台](https://console.aws.amazon.com/vpc/) 或 [Network Firewall API](https://docs.aws.amazon.com/network-firewall/latest/APIReference/) 启用多个 VPC 端点 。要了解此功能的更多信息和定价，请参阅 AWS Network Firewall [产品页面](https://aws.amazon.com/network-firewall/) 和服务 [文档](https://docs.aws.amazon.com/network-firewall/latest/developerguide/)。

---

# AWS GovCloud（美国）区域的 ENA Express

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/ena-express-govcloud-us-regions](https://aws.amazon.com/about-aws/whats-new/2025/06/ena-express-govcloud-us-regions) 

**发布时间:** 2025-06-03  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS GovCloud（美国）区域的 ENA Express  

发布日期: 2025年6月3日  

AWS 宣布推出 ENA Express，这是一款专为 AWS GovCloud（美国）区域中的 EC2 实例设计的网络接口，基于 SRD（可扩展可靠数据报）协议构建。ENA Express 是 ENA 的一项功能，通过 SRD 协议在两个关键方面提升网络性能：更高的单流带宽和更低的尾部延迟（Tail Latency），从而优化 EC2 实例之间的网络流量。  

诸如数据库、文件系统和分布式存储系统等负载需要更大的单流带宽，并且对尾部延迟的变化非常敏感。在此之前，用户可以通过多路径 TCP 提升带宽，但这会增加复杂性，有时还可能与应用层不兼容。此外，TCP 在服务器因请求过载时无法有效处理拥塞问题。SRD 是一种专有协议，通过 Nitro 卡直接提供拥塞控制、多路径传输和数据包重排序，从而实现这些改进。启用 ENA Express 非常简单，只需一条命令或在控制台中切换即可为您的 EC2 实例启用 SRD。  

借助 SRD 协议，ENA Express 提高了单流带宽的最大值，并显著改善了高吞吐量工作负载的尾部延迟。ENA Express 对应用程序完全透明，支持 TCP 和 UDP 协议。配置后，ENA Express 可以在同一个可用区（Availability Zone）内的任意两个受支持实例之间运行。  

ENA Express 现已在 AWS GovCloud（美国）区域上线，并且无需额外费用。要了解更多信息并开始使用，请查阅最新的 [EC2 文档](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ena-express.html) 。

---

# AWS Site-to-Site VPN 推出三项新功能以增强安全性

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/aws-site-to-site-vpn-three-capabilities-enhanced-security/](https://aws.amazon.com/about-aws/whats-new/2025/06/aws-site-to-site-vpn-three-capabilities-enhanced-security/) 

**发布时间:** 2025-06-03  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS Site-to-Site VPN 推出三项新功能以增强安全性  

发布日期: 2025 年 6 月 3 日  

AWS Site-to-Site VPN 是一项完全托管的服务，允许您通过 IP 安全协议 (IPSec) 隧道在您的数据中心或分支机构与 AWS 资源之间建立安全连接。现在，该服务新增了三项功能，以提升安全性并简化配置。  

- **AWS Secrets Manager 集成:** 通过集成 AWS Secrets Manager，当用户将预共享密钥 (PSKs) 存储在 Secrets Manager 中时，VPN 连接 API 的响应将隐藏 PSK，并显示 Secrets Manager 的 ARN（Amazon Resource Name），从而提供更高的安全性。  
- **用于跟踪 VPN 算法的新 API:** 您现在可以使用 “GetActiveVpnTunnelStatus” API 轻松跟踪当前协商的互联网密钥交换 (IKE) 版本、Diffie-Hellman (DH) 组、加密算法和完整性算法。这一新 API 消除了启用 Site-to-Site VPN 日志的需求，节省时间并降低运维负担。  
- **推荐配置:** “GetVpnConnectionDeviceSampleConfiguration” API 新增了 “recommended” 参数，帮助您在客户网关设备上应用最佳实践的安全配置 - IKE 版本 2、DH 组 20、SHA-384 完整性算法以及 AES-GCM-256 加密算法，减少配置时间和潜在错误。  

使用这些功能无需额外费用。这些功能已在所有提供 AWS Site-to-Site VPN 服务的 AWS 商业区域上线，但欧洲（米兰）区域除外。如需了解更多信息并开始使用，请访问 AWS Site-to-Site VPN [文档](https://docs.aws.amazon.com/vpn/latest/s2svpn/enhanced-security.html) 。

---

# Amazon API Gateway 推出 REST API 的路由规则功能

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-api-gateway-routing-rules-rest-apis/](https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-api-gateway-routing-rules-rest-apis/) 

**发布时间:** 2025-06-03  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon API Gateway 推出 REST API 的路由规则功能  

发布日期: 2025年6月3日  

Amazon API Gateway 现在支持通过自定义域名 (Custom Domain Names) 为 REST API 配置路由规则。这一新功能允许您根据 HTTP 头部值、URL 基础路径，或两者的组合动态路由传入请求。  

这种灵活性支持多种应用场景，包括 A/B 测试 (A/B Testing)、API 版本控制 (API Versioning) 和动态后端选择 (Dynamic Backend Selection)。要使用此功能，您需要通过设置优先级、定义条件（HTTP 头部、URL 路径或两者结合）并关联操作来配置路由规则。API Gateway 按优先级顺序评估这些规则，数字越小优先级越高。当请求满足某条规则的所有条件时，API Gateway 将其路由到配置的 REST API ID 和阶段 (Stage)。通过在 API Gateway 内直接实现路由逻辑，您可以消除代理层和复杂的 URL 结构，同时保持对 API 流量的精细路由控制。此功能支持公共和私有 REST API，并与现有的 API 映射 (API Mappings) 兼容。  

自定义域名的路由规则功能已在所有 [AWS 区域](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 推出，包括 AWS GovCloud（美国）区域。如需了解更多信息，请参阅 [博客文章](https://aws.amazon.com/blogs/compute/dynamically-routing-requests-with-amazon-api-gateway-routing-rules/) 和 [API Gateway 文档](https://docs.aws.amazon.com/apigateway/latest/developerguide/rest-api-routing-mode.html)。

---

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-vpc-route-server-logging-enhancements/](https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-vpc-route-server-logging-enhancements/)  

**发布时间:** 2025-06-03  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon VPC Route Server 宣布日志增强功能  

发布于：2025 年 6 月 3 日  

Amazon VPC Route Server 通过新增网络指标增强了连接性监控和日志记录。这些指标使客户能够主动监控网络健康、排查网络问题，并获取路由传播和对等连接的可见性。  
  
此前，客户需要手动跟踪边界网关协议 (BGP) 和双向转发检测 (BFD) 会话变化，并经常需要 AWS 支持协助进行网络故障排除。通过这些新的日志功能，客户可以独立监控和诊断网络连接问题，从而实现更快的解决时间和更好的网络可见性。该增强功能提供了 BGP 和 BFD 会话状态的实时监控、历史对等会话数据日志记录，以及通过 CloudWatch、Amazon S3、Amazon Data Firehose 或 AWS CLI 的灵活日志交付选项。  
  
VPC Route Server 的增强日志记录可在所有支持 VPC Route Server 的 AWS 商业区域中使用。对于 Amazon CloudWatch、Amazon S3 和 Amazon Data Firehose 的售卖日志，将收取数据费用。要了解更多关于此功能的信息，请参阅我们的 [文档](https://docs.aws.amazon.com/vpc/latest/userguide/route-server-peer-logging.html) 。

---

# ENA Express 支持 120 个新实例

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/ena-express-new-instances](https://aws.amazon.com/about-aws/whats-new/2025/06/ena-express-new-instances)

**发布时间:** 2025-06-04

**厂商:** AWS

**类型:** WHATSNEW

---
# ENA Express 支持 120 个新实例 

发表于: 2025 年 6 月 4 日 

120 个 EC2 实例 (EC2 instances) 现已支持 ENA Express，包括网络优化实例 (network optimized instances)、存储实例 (storage instances)、高内存实例 (high-memory instances) 和加速计算实例 (accelerated computing instances)。此次发布中，ENA Express 新增了对 35 个网络优化实例、6 个存储实例、7 个高内存实例和 5 个加速计算实例的支持。此外，ENA Express 还为 67 个不同的计算型 (compute)、通用型 (general purpose) 和内存优化 EC2 实例添加了支持。  
  
ENA Express 是一个网络功能，使用 AWS 可伸缩可靠数据报 (SRD) 协议，通过两种关键方式提升 EC2 实例之间的网络性能：更高的单个流带宽和更低的尾部延迟 (tail latency)。SRD 是一个专有协议，通过高级拥塞控制、多路径传输和直接从 Nitro 卡 (Nitro card) 进行的包重新排序来实现这些改进。ENA Express 对您的应用程序是透明的，支持 TCP 和 UDP 协议。  
  
ENA Express 与网络优化实例结合，适合需要更高单个流带宽和一致尾部延迟的文件系统和媒体编码工作负载。ENA Express 与存储实例结合，可提升数据库的大对象事务性能。ENA Express 在高内存实例上，适用于如 SAP HANA 这样的内存数据库事务的单个流性能。最后，对于加速计算实例，ENA Express 可提供更好的单个流性能，用于访问像 FSx Lustre 这样的文件系统服务。  
  
ENA Express 在所有 AWS 商业区域 (AWS Commercial Regions) 和 AWS GovCloud (US) 区域中可用，且无需额外费用。有关完整支持实例列表，请查看最新的 [EC2 文档](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ena-express.html)。

---

# AWS Network Firewall 推出新监控仪表板 (monitoring dashboard)

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/aws-network-firewall-monitoring-dashboard](https://aws.amazon.com/about-aws/whats-new/2025/06/aws-network-firewall-monitoring-dashboard)  

**发布时间:** 2025-06-04  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS Network Firewall 推出新监控仪表板  

发表于: 2025 年 6 月 4 日  

今天，AWS 宣布在 AWS Network Firewall 控制台中推出一个新监控仪表板 (monitoring dashboard)，从而提升客户监控网络流量 (network traffic) 的能力。这个新功能提供了对网络活动的可见性，有助于更有效地管理和排查防火墙配置 (firewall configurations)。  
  
新监控仪表板 (monitoring dashboard) 提供了有价值的流量模式洞见，包括顶级流量流 (top traffic flows)、TLS 服务器名称指示 (SNI) 以及 HTTP Host 标头 (HTTP Host headers)。这种详细程度让客户能够快速识别和分析其最重要的网络互动。此外，该仪表板还显示了长寿命 TCP 流 (long-lived TCP flows) 和 TCP 握手失败的流量流 (traffic flows where TCP handshake failed)，这对于排查网络问题和识别潜在安全风险特别实用。  
  
这个新监控仪表板 (monitoring dashboard) 在所有支持 AWS Network Firewall 的 AWS 区域 (AWS Regions) 中可用，[查看 AWS 区域表](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/)。使用该仪表板不会产生额外的 AWS Network Firewall 费用。请查看 Amazon CloudWatch [定价](https://aws.amazon.com/cloudwatch/pricing/) 或 Amazon Athena [定价](https://aws.amazon.com/athena/pricing/)，以了解与日志 (Logs) 和查询 (Queries) 相关的费用。  
  
要利用这个新功能，客户需要在 AWS Network Firewall 中配置流量日志 (Flow logs) 和警报日志 (Alert logs)，并启用监控仪表板 (monitoring dashboard)。有关如何设置和使用新监控仪表板的更多信息，请访问 [AWS Network Firewall 文档](https://docs.aws.amazon.com/network-firewall/latest/developerguide/what-is-aws-network-firewall.html) 或登录 AWS 管理控制台 (AWS Management Console)。

---

# AWS 宣布在中华民国 (ROC) 台北新增 AWS Direct Connect 位置并扩展

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/aws-direct-connect-location-taipei-republic-of-china/](https://aws.amazon.com/about-aws/whats-new/2025/06/aws-direct-connect-location-taipei-republic-of-china/)

**发布时间:** 2025-06-05

**厂商:** AWS

**类型:** WHATSNEW

---

# AWS 宣布在中华民国 (ROC) 台北新增 AWS Direct Connect 位置并扩展

发布时间: 2025 年 6 月 5 日

今天，AWS 宣布在台北附近 Chief Telecom HD 数据中心开设一个新的 [AWS Direct Connect](https://aws.amazon.com/directconnect) 位置。通过在新的位置将您的网络连接到 AWS，您可以获得对所有公共 AWS 区域（除中国区域外）、AWS GovCloud 区域以及 [AWS 本地扩展区域 (Local Zones)](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) 的私有直接访问。该位置是中华民国 (ROC) 内的第三个 AWS Direct Connect 位置。该 Direct Connect 位置提供专用的 10 Gbps 和 100 Gbps 连接，并支持 MACsec 加密。

AWS 还宣布在台北附近现有的 Chunghwa Telecom 数据中心添加 10 Gbps 和 100 Gbps MACsec 服务。

Direct Connect 服务让您能够在 AWS 与您的数据中心、办公室或联合托管环境之间建立私有物理网络连接。这些私有连接可以提供比通过公共互联网连接更稳定的网络体验。

要了解更多关于全球 Direct Connect 位置的信息，请访问 Direct Connect [位置](https://aws.amazon.com/directconnect/locations/) 部分或 [产品详情页面](https://aws.amazon.com/directconnect)。或者，访问我们的 [入门页面](https://aws.amazon.com/directconnect/getting-started/)，了解如何购买和部署 Direct Connect。

---

# AWS Cloud WAN 通过安全组 (Security Group) 引用和增强的 DNS 支持简化网络操作

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/aws-cloud-wan-network-operations-security-referencing-dns/](https://aws.amazon.com/about-aws/whats-new/2025/06/aws-cloud-wan-network-operations-security-referencing-dns/)

**发布时间:** 2025-06-11

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Cloud WAN 通过安全组 (Security Group) 引用和增强的 DNS 支持简化网络操作

发布日期：2025 年 6 月 11 日 

AWS 宣布安全组 (Security Group) 引用和增强的域名系统 (Domain Name System, DNS) 支持在由 AWS Cloud WAN 连接的 Amazon 虚拟私有云 (VPCs) 中正式可用。通过安全组引用，客户可以简化安全组的管理，并提升通过 Cloud WAN 实现跨 VPC 连接的安全态势。通过增强的 DNS 支持，客户可以启用从附加到 Cloud WAN 的 VPC 发送的 DNS 查询，将公共 DNS 主机名解析为私有 IP 地址。  
  
客户可以通过指定基于 IP 地址、前缀列表 (Prefix-Lists)、端口和安全组引用的规则列表来配置安全组。在此之前，客户无法使用安全组引用来控制通过 Cloud WAN 连接的 VPC 之间的流量。安全组引用允许客户在入站安全规则中指定其他安全组作为引用或匹配标准，从而允许实例间流量。该功能让客户无需在应用扩展或 IP 地址变化时重新配置安全规则。包含安全组引用的规则还提供更高的可扩展性，因为一条规则可以覆盖数千个实例，并防止客户超出安全组规则限制。安全组引用和增强的 DNS 支持都是 Cloud WAN 的区域功能，这意味着 VPC 必须连接到同一个核心网络边缘 (CNE) 才能使用这些功能。  
  
安全组引用和增强的 DNS 支持在所有 [AWS 区域](https://docs.aws.amazon.com/network-manager/latest/cloudwan/what-is-cloudwan.html#cloudwan-available-regions) 中可用，前提是 Cloud WAN 已可用。您可以使用 AWS 管理控制台、AWS 命令行界面 (CLI) 和 AWS 软件开发工具包 (SDK) 启用这些功能。启用安全组引用或 DNS 支持不会产生额外费用。有关更多信息，请参阅 AWS Cloud WAN [文档页面](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-vpc-attachment.html)。

---

# Amazon VPC IP Address Manager 现已在亚太地区 (Taipei) 可用

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-vpc-ip-address-manager-asia-pacific-taipei-region](https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-vpc-ip-address-manager-asia-pacific-taipei-region)  

**发布时间:** 2025-06-13  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon VPC IP Address Manager 现已在亚太地区 (Taipei) 可用  

发表于: 2025 年 6 月 13 日  

Amazon Virtual Private Cloud [IP Address Manager (Amazon VPC IPAM)](https://docs.aws.amazon.com/vpc/latest/ipam/what-it-is-ipam.html) 可以让您更轻松地规划、跟踪和监控 AWS 工作负载的 IP 地址，现在已在亚太地区 (Taipei) 可用。  
  
Amazon VPC IPAM 允许您根据路由和安全需求轻松组织 IP 地址，并设置简单的业务规则来管理 IP 地址分配。使用 Amazon VPC IPAM，您可以自动为 Amazon VPC 和 VPC 子网分配 IP 地址，从而无需使用基于电子表格或自制 IP 地址规划应用程序，这些应用程序可能难以维护且耗时。  
  
通过此次扩展，Amazon VPC IPAM 已在所有 [AWS 区域 (AWS Regions)](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 可用，包括中国 (北京，由 Sinnet 运营)、中国 (宁夏，由 NWCD 运营) 以及 AWS GovCloud (US) 区域。  
  
要了解更多关于 IPAM 的信息，请查看 [IPAM 文档 (IPAM documentation)](https://docs.aws.amazon.com/vpc/latest/ipam/what-it-is-ipam.html)。有关定价详情，请参考 [Amazon VPC 定价页面 (Amazon VPC Pricing Page)](https://aws.amazon.com/vpc/pricing/) 中的 IPAM 选项卡。

---

# AWS Network Firewall 现支持 AWS Transit Gateway 原生集成

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/aws-network-firewall-transit-gateway-native-integration/](https://aws.amazon.com/about-aws/whats-new/2025/06/aws-network-firewall-transit-gateway-native-integration/)

**发布时间:** 2025-06-16

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Network Firewall 现支持 AWS Transit Gateway 原生集成

发布于：2025 年 6 月 16 日 

[AWS Network Firewall](https://aws.amazon.com/network-firewall/) 现支持与 [AWS Transit Gateway](https://aws.amazon.com/transit-gateway/) 的原生集成 ，以简化全球 AWS 基础设施中网络安全部署和管理。该功能已在 5 个 AWS 区域 (AWS Regions) 可用 ，让客户更高效地实施安全控制。  
  
AWS Transit Gateway 用于互联您的 Amazon 虚拟私有云 (VPCs) 和本地网络 ，而 AWS Network Firewall 则为这些 VPC 提供全面的安全控制。原生附件简化了这些服务的连接 ，提供集中式安全控制，而无需复杂的 VPC 配置。此外 ，您可以配置一个或多个可用区 (AZs) 以实现高可用性 ，确保流量在同一可用区内保持畅通。  
  
此集成可在以下 [AWS Regions](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 中使用：非洲 (开普敦) 、亚太 (海得拉巴) 、欧洲 (斯德哥尔摩) 、欧洲 (苏黎世) 和中东 (阿联酋) 。此原生集成不产生额外费用 ，仅按 [AWS Network Firewall](https://aws.amazon.com/network-firewall/pricing/) 和 [AWS Transit Gateway](https://aws.amazon.com/transit-gateway/pricing/) 的标准定价收费。  
  
要开始使用 ，请访问 AWS Network Firewall 服务 [文档](https://docs.aws.amazon.com/network-firewall/latest/developerguide/firewall-creating.html) 。

---

# AWS Shield 发布网络安全主管（预览）

**原始链接：** [https://aws.amazon.com/about-aws/whats-new/2025/06/aws-shield-network-security-director-preview](https://aws.amazon.com/about-aws/whats-new/2025/06/aws-shield-network-security-director-preview)  

**发布时间：** 2025-06-17  

**厂商：** AWS  

**类型：** WHATSNEW  

---  

# AWS Shield 发布网络安全主管（预览）  

发布日期：2025 年 6 月 17 日  

今天，AWS Shield 宣布网络安全主管（network security director）预览版，这是一个新功能，可提供对网络中 AWS 资源的可见性，识别缺失或配置错误的网络安全服务，并推荐修复步骤。随着威胁不断演变，AWS Shield 已扩展其功能，超出 DDoS（Distributed Denial of Service）保护的范围，帮助您轻松识别需要网络和应用保护的资源，并正确保护它们。  

借助网络安全主管，AWS Shield 通过三种方式简化网络安全管理。首先，它提供网络拓扑的可见性，显示您账户中的资源及其与彼此和互联网的连接关系。它会发现启用的 AWS 网络安全服务，例如 AWS WAF（AWS Web Application Firewall）、VPC 安全组（VPC Security Groups）和 VPC 网络访问控制列表（NACLs），并根据 AWS 最佳实践和威胁情报评估它们的配置质量。其次，AWS Shield 可帮助您快速识别哪些缺失或配置错误的防火墙需要立即关注，通过显示资源上的网络安全发现结果，并按严重级别优先排序。  

最后，对于每个发现结果，您可以查看可操作的修复推荐，以正确实施或更新您使用的网络安全服务的配置。  

您可以轻松使用自然语言在 AWS 管理控制台中的 Amazon Q（Amazon Q）开发人员工具或聊天应用中，向 AWS Shield 网络安全主管提问有关网络安全配置的问题。例如，您可以询问“我的互联网面向资源中是否有任何易受 DDoS 攻击的资源？”，Amazon Q 会显示相关网络安全发现结果，包括特定资源的推荐修复步骤。此功能在预览期间免费，仅在选定的 AWS 区域提供：美国东部（北弗吉尼亚）和欧洲（斯德哥尔摩）。Amazon Q 分析网络安全配置的能力在预览期间提供于美国东部（北弗吉尼亚）。  

要了解更多信息，请访问[概述](https://aws.amazon.com/shield/) 页面。

---

# Amazon CloudFront 通过智能默认设置和自动化简化 CDN 配置

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-cloudfront-streamlines-cdn-setup-smart-defaults-automation](https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-cloudfront-streamlines-cdn-setup-smart-defaults-automation)  

**发布时间:** 2025-06-17  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon CloudFront 通过智能默认设置和自动化简化 CDN 配置  

发布时间: 2025 年 6 月 17 日  

Amazon CloudFront 引入了新的控制台 (Console) 体验，帮助您更轻松地将安全、高性能的应用交付给互联网用户。传统上，设置内容分发网络 (Content Delivery Network，CDN) 需要深入了解 CDN 配置、域名管理以及安全最佳实践。新版 CloudFront 控制台体验通过统一的方法简化了整个内容交付和安全过程。该体验会自动配置和管理 DNS 记录，使用 Amazon Route 53，以及 TLS 证书，使用 AWS Certificate Manager (ACM)。无论您的 CDN 专业知识水平如何，都能在短短 30 秒内创建安全的优化分发 (Distribution)。  
  
在创建分发时，CloudFront 会根据您的特定来源 (Origin) 类型自动应用优化设置。例如，当从 Amazon S3 服务静态网站时，CloudFront 会自动配置来源访问控制 (Origin Access Control) 以防止直接访问存储桶 (Bucket)，优化缓存设置以提升性能，并启用推荐的安全设置 - 所有这些都不需要您了解这些组件的底层技术细节。  
  
这种新上手体验让您更容易利用 AWS 的全球边缘网络 (Edge Network)，降低最终用户延迟，并提升应用的安全态势。新体验已在全球可用，且无需额外费用。要开始使用新版 CloudFront 体验，请访问 [Amazon CloudFront 控制台](https://us-east-1.console.aws.amazon.com/cloudfront/v4/home#) 或查看我们的 [文档](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.SimpleDistribution.html)。

---

# Amazon VPC 提升默认路由表容量

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-vpc-raises-default-route-table-capacity](https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-vpc-raises-default-route-table-capacity)  

**发布时间:** 2025-06-23  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon VPC 提升默认路由表容量  

发表于: 2025 年 6 月 23 日  

AWS VPC 已将每个路由表 (Route Table) 中路由的默认值从 50 条提升到 500 条。  
  
在此增强功能之前，客户需要请求限制增加，以使用超过 50 条路由的 VPC (Virtual Private Cloud) 路由表。组织通常需要更多路由来精确控制其 VPC 流量流向，例如在流量路径中插入防火墙 (Firewalls) 或网络功能 (Network Functions)，或将流量定向到对等连接 (Peering Connections)、互联网网关 (Internet Gateway)、虚拟私有网关 (Virtual Private Gateway) 或传输网关 (Transit Gateway)。此增强功能自动将路由表容量增加到 500 条路由，从而减少管理开销，并让客户无缝扩展其网络架构，以满足不断增长的需求。  
  
新默认限制将自动适用于所有 AWS 商业区域和 AWS GovCloud (US) 区域中的所有路由表。没有路由配额覆盖 (Quota Overrides) 的客户账户，将自动为现有和新建的 VPC 路由表获得 500 条路由。有路由配额覆盖的客户账户，其现有或新建 VPC 设置不会发生变化。要了解更多关于此配额增加的信息，请参考我们的 [文档](https://docs.aws.amazon.com/vpc/latest/userguide/amazon-vpc-limits.html#vpc-limits-route-tables) 。

---

# Amazon Route 53 Resolver 端点 (Resolver endpoints) 现支持私有托管区域 (private hosted zones) 的 DNS 委派

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-route-53-resolver-endpoints-dns-delegation-private-hosted-zones](https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-route-53-resolver-endpoints-dns-delegation-private-hosted-zones)  

**发布时间:** 2025-06-24  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# Amazon Route 53 Resolver 端点 (Resolver endpoints) 现支持私有托管区域 (private hosted zones) 的 DNS 委派  

发表于: 2025 年 6 月 24 日  

从今天起，域名系统 (DNS) 委派针对私有托管区域 (private hosted zones) 子域可以与 Route 53 的入站和出站 Resolver 端点 (Resolver endpoints) 一起使用。这让您可以将子域的权限从本地基础架构委派给 Route 53 Resolver 云服务，反之亦然，从而简化 AWS 和本地基础架构间的云体验。  

AWS 客户允许企业内的多个组织分别管理各自的子域和子区域，而顶层域和父托管区域通常由中央团队监督。在此之前，这些客户必须在现有网络基础架构中创建并维护条件转发规则，以让服务跨子域相互发现。然而，条件转发规则在大型组织中难以维护，而且在许多情况下，本地基础架构不支持。通过今天的发布，客户可以使用名称服务器记录将子域权限委派给 Route 53，反之亦然，从而与常见的本地 DNS 基础架构兼容，并消除团队在组织内使用条件转发规则的需要。  

Resolver 端点 (Resolver endpoints) 的入站和出站委派在全球所有 AWS 区域可用（Resolver 端点可用之处），但 AWS GovCloud 和 中国区 Amazon Web Services 除外。入站和出站委派不会额外收费，仅与 Resolver 端点 (Resolver endpoints) 使用相关。有关更多定价详情，请访问 [Route 53 定价页面](https://aws.amazon.com/route53/pricing/)；要了解此功能更多信息，请访问 [开发者指南](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/outbound-delegation-tutorial.html)。

---

# AWS 在印度尼西亚雅加达宣布 100G 扩展

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/aws-100G-expansion-jakarta-indonesia](https://aws.amazon.com/about-aws/whats-new/2025/06/aws-100G-expansion-jakarta-indonesia)  

**发布时间:** 2025-06-26  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS 在印度尼西亚雅加达宣布 100G 扩展  

发表于：2025 年 6 月 26 日  

今天，AWS 宣布在印度尼西亚雅加达附近的 NTT Jakarta 2 数据中心扩展 AWS Direct Connect 位置的 100 Gbps 专属连接。您现在可以从此位置建立到所有公共 AWS 区域（除中国区域外）、AWS GovCloud 区域以及 [AWS 本地扩展区域 (Local Zones)](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) 的私有、直接网络访问。这是雅加达的第二个提供 100 Gbps 连接并带有 MACsec 加密功能的 AWS Direct Connect 位置。  
  
Direct Connect 服务使您能够建立 AWS 和您的数据中心、办公室或联合托管环境之间的私有、物理网络连接。这些私有连接可以提供比通过公共互联网连接更一致的网络体验。  
  
有关全球超过 142 个 Direct Connect 位置的更多信息，请访问 Direct Connect [位置](https://aws.amazon.com/directconnect/locations/) 部分或 [产品详细信息页面](https://aws.amazon.com/directconnect/)。或者，访问我们的 [入门页面](https://aws.amazon.com/directconnect/getting-started/)，以了解有关如何购买和部署 Direct Connect 的更多信息。

---

# Amazon Route 53 推出 Resolver 端点的容量利用率指标

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-route-53-capacity-metric-resolver-endpoints/](https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-route-53-capacity-metric-resolver-endpoints/)  

**发布时间:** 2025-06-27  

**厂商:** AWS  

**类型:** 新功能更新  

---
# Amazon Route 53 推出 Resolver 端点的容量利用率指标  

发表于: 2025 年 6 月 27 日  

从今天起，您可以启用 Amazon CloudWatch 指标 (ResolverEndpointCapacityStatus) 来监控与您的 Amazon Virtual Private Cloud (VPC) 中的 Route 53 Resolver 端点关联的弹性网络接口 (ENIs) 的查询容量状态。新指标让您快速查看 Resolver 端点是否面临达到服务限制的风险，并采取补救措施，例如实例化额外的 ENIs 以满足容量需求。  

在今日之前，您可以启用 CloudWatch 来监控 Route 53 Resolver 端点转发的 DNS 查询数量，默认每五分钟一次，并据此估算端点何时将达到查询限制。通过此次发布，您现在可以启用新指标，直接获取 Resolver 端点容量当前状态的警报，而无需额外估算每个端点的容量。状态针对每个 Resolver 端点报告：表示端点在正常容量限制内 (0 - OK)、至少有一个 ENI 超过 50% 容量利用率 (1 - Warning)，或至少有一个 ENI 超过 75% 容量利用率 (2 - Critical)。新指标简化了 Route 53 Resolver 端点的容量管理，提供清晰、可操作的信号来支持缩放决策，而无需对查询量进行额外分析。  

要了解更多关于此发布的信息，请阅读 [文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/monitoring-resolver-with-cloudwatch.html#cloudwatch-metrics-resolver-endpoint) 或访问 [Route 53 Resolver 页面](https://aws.amazon.com/route53/resolver/)。指标本身免费，但您将因 Resolver 端点的使用产生 [费用](https://aws.amazon.com/route53/pricing/)。

---

# ARC 分区自动转移 (Zonal Autoshift) 实践 现支持按需运行和均衡容量预检查

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/arc-zonal-autoshift-practice-on-demand-runs-balanced-capacity-pre-checks](https://aws.amazon.com/about-aws/whats-new/2025/06/arc-zonal-autoshift-practice-on-demand-runs-balanced-capacity-pre-checks)

**发布时间:** 2025-06-30

**厂商:** AWS

**类型:** WHATSNEW

---
# ARC 分区自动转移 (Zonal Autoshift) 实践 现支持按需运行和均衡容量预检查

发表于: 2025 年 6 月 30 日 

分区自动转移 (Zonal Autoshift) 实践运行每周进行一次，以确保您的应用准备好应对分区转移 (Zonal shift)。现在，通过按需实践运行，您可以随时触发实践运行，并验证您的应用的准备状态。当实践运行启动时，会执行一个预检查，以确保您的应用在可用区 (AZs) 之间具有均衡容量 (Balanced capacity)。此检查适用于应用负载均衡器 (Application Load Balancers)、网络负载均衡器 (Network Load Balancers) 和 EC2 自动缩放组 (EC2 Auto Scaling groups)。  
  
要开始使用，您可以在 ARC 控制台、API 或 CLI 中启动按需实践运行。这让您可以测试应用的实践运行配置，确保警报正确设置，且应用行为符合预期。对于自动和按需实践运行，均衡容量 (Balanced capacity) 预检查会验证资源的容量，并确保启动实践运行是安全的。如果预检查失败，您会收到警报，从而采取 corrective action。  
  
分区自动转移 (Zonal Autoshift) 的按需实践运行和均衡容量 (Balanced capacity) 预检查已在 [所有商业 AWS 区域](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 以及 [AWS GovCloud (US) 区域](https://aws.amazon.com/govcloud-us/) 中可用。要了解更多，请参考 [ARC 分区自动转移文档](https://docs.aws.amazon.com/r53recovery/latest/dg/arc-zonal-autoshift.html)。

---

# AWS Global Accelerator 现已支持两个额外 AWS 区域的端点

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/06/aws-global-accelerator-endpoints-two-additional-regions/](https://aws.amazon.com/about-aws/whats-new/2025/06/aws-global-accelerator-endpoints-two-additional-regions/)  

**发布时间:** 2025-06-30  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS Global Accelerator 现已支持两个额外 AWS 区域的端点  

发表于: 2025 年 6 月 30 日  

从今天起，[AWS Global Accelerator (AWS Global Accelerator)](https://aws.amazon.com/global-accelerator/) 支持两个额外 AWS 区域的应用端点 (application endpoints)，即 AWS 墨西哥 (Central) 区域 和 亚太 (Malaysia) 区域，这将支持的 AWS 区域 (supported AWS Regions) 数量扩展到三十一个。  

AWS Global Accelerator 是一个服务，旨在帮助您提升面向互联网应用的可用性、安全性和性能。通过利用无拥塞的 AWS 网络，用户流量可获得更高的可用性、边缘处的 DDoS 保护，以及相对于公共互联网的更佳性能。Global Accelerator 提供静态 IP 地址，作为固定入口端点，用于您在 AWS 区域中的应用资源，例如 Application Load Balancers、网络负载均衡器 (Network Load Balancers)、Amazon EC2 实例 或 Elastic IPs。Global Accelerator 会持续监控应用端点的健康状态，并为多区域工作负载提供确定性的故障转移，而无需任何 DNS 依赖。  

要开始使用，请访问 AWS Global Accelerator [网站](https://aws.amazon.com/global-accelerator/) 并查看其 [文档](https://docs.aws.amazon.com/global-accelerator/)。

---

# AWS 宣布在慕尼黑开设新的 AWS 数据传输终端位置

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/07/aws-data-transfer-terminal-munich/](https://aws.amazon.com/about-aws/whats-new/2025/07/aws-data-transfer-terminal-munich/)  

**发布时间:** 2025-07-01  

**厂商:** AWS  

**类型:** WHATSNEW  

---  
# AWS 宣布在慕尼黑开设新的 AWS 数据传输终端位置  

发表于：2025 年 7 月 1 日  

今天，AWS 宣布在德国慕尼黑的 Equinix MU1 内开设新的 AWS 数据传输终端位置 (AWS Data Transfer Terminal)。这标志着 AWS 在美国以外的第一个数据传输终端，以及在欧洲的首次亮相。数据传输终端 (Data Transfer Terminal) 是一个安全的物理位置，您可以将存储设备带到这里，并使用高吞吐量网络连接上传数据到 AWS，包括 Amazon Simple Storage Service (Amazon S3)、Amazon Elastic File System (Amazon EFS) 等。  
  
数据传输终端适合需要快速、安全地将大量数据传输到 AWS 的客户。常见用例横跨多个行业和应用，包括汽车行业的先进驾驶员辅助系统 (Advanced Driver Assistance Systems) 训练数据、媒体和娱乐行业的视频制作数据处理、金融服务行业的遗留数据迁移，以及工业和农业部门的设备传感器数据上传。一旦上传，您可以立即利用 AWS 服务，如 Amazon Athena 用于分析、Amazon SageMaker 用于机器学习，或 Amazon Elastic Compute Cloud (Amazon EC2) 用于应用开发——从而将数据处理时间从数周缩短到几分钟。  
  
要了解更多，请访问数据传输终端 [产品页面](https://aws.amazon.com/data-transfer-terminal/) 和 [文档](https://docs.aws.amazon.com/datatransferterminal/latest/userguide/what-is-dtt.html)。要开始使用，请在 [AWS 控制台](https://console.aws.amazon.com/datatransferterminal) 中为您附近的数据传输终端预订。

---

# Amazon CloudFront 宣布支持 HTTPS DNS 记录

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/07/amazon-cloudfront-https-dns-records](https://aws.amazon.com/about-aws/whats-new/2025/07/amazon-cloudfront-https-dns-records)  

**发布时间:** 2025-07-01  

**厂商:** AWS  

**类型:** WHATSNEW  

---  

# Amazon CloudFront 宣布支持 HTTPS DNS 记录  

发布于: 2025 年 7 月 1 日   

今天，Amazon CloudFront 宣布支持在 Amazon Route 53 中使用 HTTPS 资源记录 (HTTPS resource records)。HTTPS 资源记录允许域名系统 (DNS) 如 Amazon Route 53 在尝试 HTTP 连接之前提供额外信息，例如支持的 HTTP 协议版本和端口号。这有助于客户端使用首选的 HTTP 协议建立初始连接，从而改善应用程序的性能和安全性。  
  
通过在 DNS 查询中使用 HTTPS DNS 记录，客户端可以发现 CloudFront 的功能，这些功能可提升应用程序的性能和安全性。例如，客户端可以识别 CloudFront 分发 (CloudFront distribution) 是否启用了 HTTP/3 (HTTP/3)，而无需在 DNS 查询后进行额外的往返时间 (RTT) 来协商 HTTP 协议。这可以减少应用程序的加载时间，尤其是在网络基础设施有限的区域。通过提前提供安全连接信息，HTTPS DNS 记录简化了与 CloudFront 分发建立安全连接的过程。此外，使用 Route 53 的客户在使用 CloudFront 别名记录时，可以免费查询 HTTPS 记录，从而降低 DNS 成本。  
  
HTTPS DNS 记录在所有边缘位置 (edge locations) 中都受支持。这不包括由 Sinnet 运营的 Amazon Web Services China (Beijing) 区域，以及由 NWCD 运营的 Amazon Web Services China (Ningxia) 区域。要了解更多关于实现此功能及其好处的细节，请阅读我们的详细 [博客文章](https://aws.amazon.com/blogs/networking-and-content-delivery/boost-application-performance-amazon-cloudfront-enables-https-record/) 。

---

# AWS 站点到站点 VPN 在更多 AWS 区域扩展 AWS Secrets Manager 集成

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/07/aws-site-to-site-vpn-secrets-manager-integration/](https://aws.amazon.com/about-aws/whats-new/2025/07/aws-site-to-site-vpn-secrets-manager-integration/)

**发布时间:** 2025-07-02

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS 站点到站点 VPN (AWS Site-to-Site VPN) 在更多 AWS 区域扩展 AWS Secrets Manager (AWS Secrets Manager) 集成

发布日期：2025 年 7 月 2 日 

AWS 站点到站点 VPN 正在扩展三个新功能，包括 AWS Secrets Manager 集成，以提升 AWS GovCloud (US) 区域 和 AWS 欧洲 (米兰) 区域 中的安全性和配置便利性。

- **AWS Secrets Manager 集成：** 当客户将预共享密钥 (PSKs) 存储在 Secrets Manager 中时，VPN 连接 API 响应会屏蔽 PSK，并改为显示 Secrets Manager ARN (Amazon Resource Name)，从而提供增强的安全性。
- **追踪 VPN 算法的新 API：** 您现在可以使用“GetActiveVpnTunnelStatus” API 轻松追踪当前协商的互联网密钥交换 (IKE) 版本、Diffie-Hellman (DH) 组、加密算法和完整性算法。此新 API 消除了启用站点到站点 VPN 日志的必要性，从而节省时间并降低操作开销。
- **推荐配置：** “GetVpnConnectionDeviceSampleConfiguration” API 现在包含“recommended” 参数，帮助您在客户网关设备上使用最佳实践安全配置 — IKE 版本 2、DH 组 20、SHA-384 完整性算法和 AES-GCM-256 加密算法 — 从而减少配置时间并避免潜在错误。

使用这些功能不会产生额外费用。要了解更多信息并开始使用，请访问 AWS 站点到站点 VPN [文档](https://docs.aws.amazon.com/vpn/latest/s2svpn/enhanced-security.html) 。

---

# Amazon VPC Lattice 宣布支持 Oracle Database@AWS

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/07/amazon-vpc-lattice-oracle-database-at-aws](https://aws.amazon.com/about-aws/whats-new/2025/07/amazon-vpc-lattice-oracle-database-at-aws) 

**发布时间:** 2025-07-08

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon VPC Lattice 宣布支持 Oracle Database@AWS

发布于: 2025-07-08

借助 Amazon VPC Lattice 对 [Oracle Database@AWS (ODB)](https://aws.amazon.com/about-aws/whats-new/2025/07/oracle-database-at-aws-now-generally-available/)  的支持，您现在可以将 VPC 和本地环境中的应用程序连接到您的 ODB 网络。您还可以利用 VPC Lattice 从您的 Oracle Exadata 工作负载中私密且安全地访问 Amazon S3 和 Amazon Redshift。

此次发布后，您的 ODB 数据库可以轻松连接到数千个 VPC 和本地环境中的 AWS 服务、HTTP API 和 TCP 应用程序，无需进行复杂的网络设置。VPC Lattice 简化了网络管理并提供了集中式可见性 (centralized visibility)。您还可以使用 ODB 托管集成 (ODB managed integrations) (由 VPC Lattice 提供支持) 来私密且安全地访问 Amazon S3 和 Amazon Redshift。只需点击几下，您就可以启用 OCI 托管备份 (OCI managed backup) 将 ODB 数据库备份到 Amazon S3，或者配置您自己的 Amazon S3 备份。此外，零 ETL 集成 (Zero-ETL integration) 可将 ODB 数据库连接到 Amazon Redshift，以分析跨多个数据库的数据。

在 Oracle Database@AWS 全面可用的所有 AWS 区域 (AWS Regions) 中，均已提供 VPC Lattice 支持。

要开始使用，请通过 AWS 管理控制台 (AWS Management Console) 预置 Oracle Database@AWS 资源。您可以使用 AWS CLI、SDK 或 AWS 管理控制台来配置 VPC Lattice 资源。要了解更多信息，请阅读[发布博客](https://aws.amazon.com/blogs/networking-and-content-delivery/oracle-databaseaws-network-connectivity-using-amazon-vpc-lattice/) 、Amazon [VPC Lattice](https://docs.aws.amazon.com/vpc-lattice/latest/ug/vpc-lattice-oci.html)  和 [Oracle Database@AWS](https://docs.aws.amazon.com/odb/latest/UserGuide/service-integrations.html)  文档。

---

# Oracle Database@AWS 宣布正式发布并扩展网络功能

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/07/oracle-database-aws-general-expands-networking-capabilities/](https://aws.amazon.com/about-aws/whats-new/2025/07/oracle-database-aws-general-expands-networking-capabilities/) 

**发布时间:** 2025-07-08

**厂商:** AWS

**类型:** WHATSNEW

---
# Oracle Database@AWS 宣布正式发布并扩展网络功能

发布于: 2025-07-08

今天，在我们 [宣布](https://aws.amazon.com/about-aws/whats-new/2025/07/oracle-database-at-aws-now-generally-available/)  Oracle Database@AWS 正式发布的同时，我们还推出了一系列全新的 AWS 网络功能，使客户能够轻松使用 Oracle Database@AWS 构建企业级应用和服务。通过本次发布，客户可以将其 Oracle Database@AWS (ODB) 网络与 VPC 和本地网络无缝连接，并能从 ODB 网络中以原生方式安全地访问 AWS 服务。

首先，客户希望能够轻松地将 ODB 网络中的 Oracle Exadata 数据库工作负载连接到 VPC 和本地网络中的应用程序。客户可以利用与 AWS Transit Gateway 的集成分层来大规模简化连接，使用 AWS Cloud WAN 连接全球网络，以及通过 Amazon VPC Lattice 实现安全的服务到服务连接 (service-to-service connectivity)，从而以最少的网络变更简化其混合网络连接。其次，客户希望能够将其数据库备份发布到自己的 S3 存储桶中。借助由 Amazon VPC Lattice 提供支持的 ODB 网络与 AWS 服务之间的原生连接，客户可以从 ODB 网络建立到 Amazon S3 的私密且安全的访问。最后，客户希望通过在不同的 AWS 账户中启动其 Oracle Exadata 数据库和应用程序来保持强大的安全性与资源隔离 (resource isolation)，同时通过对等连接 (peering) 实现低延迟连接。现在，客户可以使用 AWS RAM 集成来支持跨账户对等连接。这些集成使客户能够在 AWS 内部迁移和运行 Oracle Exadata Database Service 和 Oracle Autonomous Database on Dedicated Exadata infrastructure 上的生产工作负载。

Oracle Database@AWS 的网络功能现已在美国东部 (弗吉尼亚北部) 和美国西部 (俄勒冈) AWS 区域 (AWS Regions) 推出。客户可以使用 AWS 管理控制台 (AWS Management Console) 开始预置和管理其 Oracle Database@AWS 资源。要了解有关网络功能的更多信息，请参阅 [博客](https://aws.amazon.com/blogs/networking-and-content-delivery/oracle-databaseaws-network-connectivity-using-amazon-vpc-lattice/)  和 [文档](https://docs.aws.amazon.com/odb/latest/UserGuide/what-is-odb.html) 。有关定价信息，请参阅各项集成的产品 [页面](https://aws.amazon.com/products/networking/) 。

---

# Amazon VPC 现已支持针对大型 IP 池的 IPv4 入口路由

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/08/ipv4-ingress-routing/](https://aws.amazon.com/about-aws/whats-new/2025/08/ipv4-ingress-routing/) 

**发布时间:** 2025-08-15

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon VPC 现已支持针对大型 IP 池的 IPv4 入口路由

发布于: 2025年8月15日

Amazon VPC 现允许客户将发往大型公有 IP 地址池的入站互联网流量路由到 VPC 内的单个弹性网络接口 (ENI)。
  
在此增强功能发布之前，互联网网关只接受发往与 VPC 中网络接口关联的公有 IP 地址的流量。可与网络接口关联的 IP 地址数量存在限制。这些限制取决于实例类型，具体信息请参阅我们的 [文档](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AvailableIpPerENI.html) 。在电信 (Telco)、物联网 (IoT) 和其他行业中，存在一些用例需要客户将发往超出允许限制的大型公有 IP 池的入站流量路由到单个网络接口。此前，客户需要执行地址转换来整合如此大量 IP 地址的流量。这项增强功能消除了在这些电信和物联网用例中对入站互联网连接执行地址转换的需求。客户可以自带公有 IP 池 ([BYOIP 文档](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-byoip.html) )，并配置其 VPC 互联网网关以接受属于该 BYOIP 池的流量，并将其路由到网络接口。他们还可以将此功能与 VPC Route Server 结合使用，在发生故障时动态更新路由。有关 VPC Route Server 的详细信息，请参阅我们的 [公开文档](https://docs.aws.amazon.com/vpc/latest/userguide/dynamic-routing-route-server.html) 。
  
此增强功能现已在所有 AWS 商业、AWS 中国和 GovCloud 区域推出。要了解有关此功能的更多信息，请参阅我们的 [文档](https://docs.aws.amazon.com/vpc/latest/userguide/advanced-routing.html) 。

---

# AWS Direct Connect 宣布在西班牙巴塞罗那设立新站点

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/08/aws-direct-connect-barcelona-spain/](https://aws.amazon.com/about-aws/whats-new/2025/08/aws-direct-connect-barcelona-spain/) 

**发布时间:** 2025-08-18

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Direct Connect 宣布在西班牙巴塞罗那设立新站点

发布于：2025年8月18日

今日，AWS 宣布在西班牙巴塞罗那附近的 Equinix BA1 数据中心内，启用一个新的 [AWS Direct Connect](https://aws.amazon.com/directconnect) 站点。现在，您可以通过该站点建立私有的直接网络连接，接入所有公共 AWS 区域 (中国区除外)、AWS GovCloud 区域以及 [AWS 本地扩展区域 (Local Zones)](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) 。该站点是 AWS Direct Connect 在巴塞罗那设立的第一个站点，也是在西班牙境内的第三个站点。该 Direct Connect 站点提供专用的 10 Gbps 和 100 Gbps 连接，并支持 MACsec 加密。

Direct Connect 服务使您能够在 AWS 与您的数据中心、办公室或主机托管环境之间建立私有的物理网络连接。与通过公共互联网建立的连接相比，这些私有连接可以提供更稳定的网络体验。

要了解全球超过 143 个 Direct Connect 站点的更多信息，请访问 Direct Connect [产品详情页面](https://aws.amazon.com/directconnect) 中的 [站点](https://aws.amazon.com/directconnect/locations/) 部分。或者，访问我们的 [入门指南](https://aws.amazon.com/directconnect/getting-started/) 页面，了解如何购买和部署 Direct Connect。

---

# Amazon VPC IPAM 新增控制台内 CloudWatch 警报管理功能

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/08/amazon-vpc-ipam-console-cloudwatch-alarm-management](https://aws.amazon.com/about-aws/whats-new/2025/08/amazon-vpc-ipam-console-cloudwatch-alarm-management)

**发布时间:** 2025-08-21

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon VPC IPAM 新增控制台内 CloudWatch 警报管理功能

发布于: 2025-08-21

今日，Amazon Web Services 宣布为其 Amazon VPC IP 地址管理器 (IPAM) 改进了 Amazon CloudWatch 警报集成。这项增强功能让您可以直接在 IPAM 控制台中更好地查看和管理现有的 CloudWatch 警报。通过这项新集成，您可以快速识别潜在的 IP 地址管理问题，并在整个组织内采取主动措施。

这项增强的集成将与 IPAM 相关的 CloudWatch 警报直接引入 IPAM 控制台，为所有 IPAM 页面提供了统一的警报状态视图。这种可见性有助于快速响应潜在的 IP 地址管理问题。您现在可以直接从 IPAM 控制台创建 CloudWatch 警报——点击“创建警报”选项将跳转到 CloudWatch，并预先填充相关字段，从而简化了 IP 使用率警报的设置。新增的资源级别“Alarms”选项卡为与特定 IPAM 资源关联的所有警报提供了全面的可见性，使您能更轻松、有效地管理和监控您的 IP 地址空间。

这项改进的集成对于管理 IP 地址空间的网络团队尤其有价值，因为它通过提供更好的可见性和更简便的现有警报管理来帮助预防问题。控制台还为没有关联警报的资源提供主动监控建议，有助于确保您的 IP 地址管理基础设施实现全面的监控覆盖。

该功能现已在所有支持 Amazon VPC IPAM 的 [*AWS 区域*](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 上线，包括 AWS 中国区域和 AWS GovCloud (US) 区域。

要了解更多关于使用 CloudWatch 监控 IPAM 的信息，请查阅 [CloudWatch IPAM 文档](https://docs.aws.amazon.com/vpc/latest/ipam/cloudwatch-ipam.html) 。有关定价详情，请参阅 [Amazon VPC 定价页面](https://aws.amazon.com/vpc/pricing/) 上的 IPAM 选项卡。

---

# AWS Client VPN 现已支持连接到 IPv6 资源

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/08/aws-client-vpn-connectivity-ipv6-resources](https://aws.amazon.com/about-aws/whats-new/2025/08/aws-client-vpn-connectivity-ipv6-resources) 

**发布时间:** 2025-08-26

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Client VPN 现已支持连接到 IPv6 资源

发布于: 2025 年 8 月 26 日

今天，AWS Client VPN 宣布支持对 IPv6 工作负载的远程访问，允许客户建立到其已启用 IPv6 的 VPC 资源的安全 VPN 连接。这项新功能使客户能够满足其合规性和 IPv6 网络采用目标。现在，企业可以通过其 Client VPN 终端节点 (endpoints) 支持 IPv4、IPv6 和双栈 (dual-stack) 资源的连接。

此前，Client VPN 仅支持对启用 IPv4 的 AWS 工作负载的远程访问。借助此功能，管理员现在可以使用纯 IPv6 或双栈 Client VPN 终端节点来支持启用 IPv6 的资源。企业现在可以将其远程用户直接连接到 IPv6 资源，并保持端到端 (end-to-end) 的纯 IPv6 连接。例如，企业现在可以使用支持 IPv6 的设备，通过 Client VPN 远程访问 VPC 中已启用 IPv6 的资源，从而保持端到端的 IPv6 连接。此功能在保留原生协议偏好的同时，简化了使用 IPv6 的企业的网络架构。

此功能已在 AWS Client VPN 正式可用的所有区域 (regions) 提供，中东 (巴林) 区域除外，且不产生额外费用。客户可以按当前终端节点的每小时价格使用 IPv6 和双栈终端节点。

要了解有关 Client VPN 的更多信息：
- 访问 AWS Client VPN [产品页面](https://aws.amazon.com/vpn/) 
- 阅读 AWS Client VPN [文档](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/what-is.html) 
- 阅读 AWS Client VPN [用户指南](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/client-vpn-user-what-is.html)

---

# AWS Client VPN 将操作系统支持扩展至 Windows Arm64 v5.3.0

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/08/aws-client-vpn-windows-arm64/](https://aws.amazon.com/about-aws/whats-new/2025/08/aws-client-vpn-windows-arm64/) 

**发布时间:** 2025-08-27

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Client VPN 将操作系统支持扩展至 Windows Arm64 v5.3.0

发布于: 2025 年 8 月 27 日

AWS Client VPN 现已通过 5.3.0 版本支持 Windows Arm64 客户端。您现在可以在最新的 Windows Arm64 操作系统版本上运行 AWS 提供的 VPN 客户端。AWS Client VPN 桌面客户端可免费使用，并可在此处 [下载](https://aws.amazon.com/vpn/client-vpn-download/) 。

AWS Client VPN 是一项托管服务 (managed service)，可将您的远程工作人员安全地连接到 AWS 或本地 (on-premises) 网络。它支持适用于 MacOS、Windows x64、Windows Arm64 和 Ubuntu-Linux 的桌面客户端。通过此次发布，Client VPN 现已支持 Windows Arm64 5.3.0。它已经支持 Mac OS 13.0、14.0 和 15.0 版本，Windows 10 (x64) 和 Windows 11 (Arm64 和 x64)，以及 Ubuntu Linux 22.04 和 24.04 LTS 版本。

此客户端版本在所有已正式推出 (generally available) AWS Client VPN 的区域 (regions) 均可使用，无需额外费用。

要了解有关 Client VPN 的更多信息：
- 访问 AWS Client VPN [产品页面](https://aws.amazon.com/vpn/) 
- 阅读 AWS Client VPN [文档](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/what-is.html) 
- 阅读 AWS Client VPN [用户指南](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/client-vpn-user-what-is.html)

---

# AWS 扩展流量镜像 (Traffic Mirroring) 对新实例类型的支持
发布于：2025 年 8 月 28 日
Amazon Virtual Private Cloud (Amazon VPC) 流量镜像 (Traffic Mirroring) 现已支持更多实例类型。Amazon VPC 流量镜像允许您将 VPC 内 EC2 实例的网络流量复制到安全和监控设备，以用于内容检测、威胁监控和故障排除等场景。
此次发布后，您可以在所有 Nitro v4 实例上启用 VPC 流量镜像。您可以在我们的 [文档](https://docs.aws.amazon.com/vpc/latest/mirroring/what-is-traffic-mirroring.html#supported-instance-types) 中查看支持 VPC 流量镜像的完整实例列表。您也可以在我们的 [AWS Nitro 系统文档](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-nitro-instances.html) 中查看基于不同 Nitro 系统版本构建的实例的完整列表。
所有区域新增的这些实例类型均支持 VPC 流量镜像。要了解有关 VPC 流量镜像的更多信息，请访问 VPC 流量镜像 [文档](https://docs.aws.amazon.com/vpc/latest/mirroring/what-is-traffic-mirroring.html)。

---

# AWS Direct Connect 宣布在尼日利亚拉各斯进行 100G 扩容
**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/aws-direct-connect-100g-expansion-lagos/](https://aws.amazon.com/about-aws/whats-new/2025/09/aws-direct-connect-100g-expansion-lagos/) 
**发布时间:** 2025-09-02
**厂商:** AWS
**类型:** WHATSNEW
---
# AWS Direct Connect 宣布在尼日利亚拉各斯进行 100G 扩容
发布于: 2025-09-02

今天，AWS 宣布在尼日利亚拉各斯附近的 Rack Centre LGS1 数据中心，对现有的 [AWS Direct Connect](https://aws.amazon.com/directconnect) 站点 进行了扩展，新增了具备 MACsec 加密功能的 10 Gbps 和 100 Gbps 专用连接。您现在可以从该站点建立到所有公共 AWS 区域 (中国区除外)、AWS GovCloud 区域和 [AWS 本地扩展区域 (Local Zones)](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) 的私有直接网络访问。

Direct Connect 服务使您能够在 AWS 与您的数据中心、办公室或主机托管环境之间建立私有的物理网络连接。与通过公共互联网建立的连接相比，这些私有连接可以提供更一致的网络体验。

要了解全球超过 145 个 Direct Connect 站点的更多信息，请访问 Direct Connect [产品详情页面](https://aws.amazon.com/directconnect) 的 [位置](https://aws.amazon.com/directconnect/locations/) 部分。或者，访问我们的 [入门](https://aws.amazon.com/directconnect/getting-started/) 页面，了解有关如何购买和部署 Direct Connect 的更多信息。

---

# AWS Control Tower 现已支持互联网协议第 6 版 (IPv6)

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/aws-control-tower-supports-internet-protocol-version-6](https://aws.amazon.com/about-aws/whats-new/2025/09/aws-control-tower-supports-internet-protocol-version-6) 

**发布时间:** 2025-09-02

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Control Tower 现已支持互联网协议第 6 版 (IPv6)

发布于: 2025年9月2日

AWS Control Tower 和 Control Catalog API 现已允许客户使用互联网协议第 6 版 (IPv6) 地址。借助新的双栈 (dual-stack) 终端节点，客户可以使用 IPv6、IPv4 或双栈客户端通过公有互联网连接到 AWS Control Tower。为实现向后兼容性，现有的支持 IPv4 的 AWS Control Tower 终端节点将继续可用。

互联网的持续发展，尤其是在移动应用、互联设备和物联网 (IoT) 领域的增长，推动了整个行业向 IPv6 的迁移。IPv6 将可用地址数量增加了几个数量级，因此客户将不再需要在其 Amazon Virtual Private Cloud (Amazon VPC) 中管理重叠的地址空间。

AWS Control Tower 和 Control Catalog API 对 IPv6 的支持已在所有提供 AWS Control Tower 和 Control Catalog API 的区域上线。有关 AWS Control Tower 可用区域的完整列表，请参阅 [AWS 区域表](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 。要了解有关在您的环境中配置 IPv6 的最佳实践，请访问 [ *关于在 AWS 上使用 IPv6 的白皮书*](https://docs.aws.amazon.com/whitepapers/latest/ipv6-on-aws/internet-protocol-version-6.html) 。要了解有关 AWS Control Tower 的更多信息，请访问 [AWS Control Tower 用户指南](https://docs.aws.amazon.com/controltower/latest/userguide/what-is-control-tower.html) 。

---

# AWS Direct Connect 宣布在新西兰奥克兰设立新站点

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/aws-direct-connect-auckland/](https://aws.amazon.com/about-aws/whats-new/2025/09/aws-direct-connect-auckland/) 
**发布时间:** 2025-09-02
**厂商:** AWS
**类型:** WHATSNEW
---
# AWS Direct Connect 宣布在新西兰奥克兰设立新站点
发布于: 2025 年 9 月 2 日

今天，作为 AWS 亚太 (新西兰) 区域发布的一部分，AWS 宣布在新西兰奥克兰附近的 Spark Digital Mayoral Drive Exchange (MDR) 数据中心内启用一个新的 AWS Direct Connect 站点。现在，您可以通过该站点建立到所有公共 AWS 区域 (中国区除外)、AWS GovCloud 区域和 AWS 本地扩展区域 (Local Zones) 的私有直接网络访问。该 Direct Connect 站点提供专用的 10 Gbps 和 100 Gbps 连接，并支持 MACsec 加密。

Direct Connect 服务使您能够在 AWS 与您的数据中心、办公室或主机托管环境之间建立私有的物理网络连接。与通过公共互联网建立的连接相比，这些私有连接可以提供更一致的网络体验。

有关全球超过 144 个 Direct Connect 站点的更多信息，请访问 Direct Connect [产品详情页面](https://aws.amazon.com/directconnect) 的 [站点](https://aws.amazon.com/directconnect/locations/) 部分。或者，访问我们的 [入门](https://aws.amazon.com/directconnect/getting-started/) 页面，了解如何购买和部署 Direct Connect。

---

# AWS Direct Connect 宣布在肯尼亚内罗毕设立新站点

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/aws-direct-connect-nairobi/](https://aws.amazon.com/about-aws/whats-new/2025/09/aws-direct-connect-nairobi/) 

**发布时间:** 2025-09-03

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Direct Connect 宣布在肯尼亚内罗毕设立新站点

发布日期: 2025 年 9 月 3 日

今天，AWS 宣布在肯尼亚内罗毕附近的 East African Data Centres NBO1 数据中心内，启用一个新的 [AWS Direct Connect](https://aws.amazon.com/directconnect) 站点。 您现在可以从该站点建立到所有公共 AWS 区域 (中国区域除外)、AWS GovCloud 区域和 [本地扩展区域 (AWS Local Zones)](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) 的私有、直接的网络访问。 该站点是肯尼亚的首个 AWS Direct Connect 站点。 该 Direct Connect 站点提供专用的 10 Gbps 和 100 Gbps 连接，并支持 MACsec 加密。

Direct Connect 服务使您能够在 AWS 与您的数据中心、办公室或主机托管环境之间建立私有的物理网络连接。 与通过公共互联网建立的连接相比，这些私有连接可以提供更一致的网络体验。

要了解全球超过 145 个 Direct Connect 站点的更多信息，请访问 Direct Connect [产品详情页面](https://aws.amazon.com/directconnect) 的 [站点](https://aws.amazon.com/directconnect/locations/) 部分。 或者，访问我们的 [入门指南](https://aws.amazon.com/directconnect/getting-started/) 页面，了解如何购买和部署 Direct Connect。

---

# Amazon CloudFront 发布支持后量子加密的 TLS 安全策略

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-cloudfront-TLS-policy-post-quantum-support](https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-cloudfront-TLS-policy-post-quantum-support) 

**发布时间:** 2025-09-05

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon CloudFront 发布支持后量子加密的 TLS 安全策略

发布于: 2025-09-05

Amazon CloudFront 宣布在所有现有的传输层安全 (Transport Layer Security, TLS) 安全策略中支持混合后量子密钥协商 (hybrid post-quantum key establishment)，为客户端到边缘站点的连接提供增强的保护，以抵御未来的量子计算威胁。此外，CloudFront 还推出了一项新的仅支持 TLS 1.3 的安全策略，增强了查看器与边缘站点之间的 TLS 选项。这些更新使客户能够利用抗量子加密技术，同时在配置其 CloudFront 分配时拥有更大的灵活性，以满足特定的安全与合规性要求。

后量子密码学 (post-quantum cryptography, PQC) 功能已为客户端到边缘站点的连接自动启用，提供了面向未来的加密技术，可确保长期的数据安全并为满足监管合规性做好准备。默认情况下，所有现有的安全策略都支持 PQC，无需客户进行任何配置。新的 TLS1.3_2025 策略仅支持 TLS 1.3，使客户能够利用最新的 TLS 协议，与早期 TLS 版本相比，该协议提供了更高的安全性和性能。这对于强制执行最新安全标准的组织尤其有用。

这些 PQC 功能和新的安全策略已在所有 CloudFront 边缘站点可用。使用 PQC 或 TLS1.3_2025 策略不会产生额外费用。要了解有关后量子密码学和这项新 TLS 策略的更多信息，以及如何在您的 CloudFront 分配中实施它们，请访问 CloudFront 文档。 [CloudFront 文档](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/secure-connections-supported-viewer-protocols-ciphers.html) 。

---

# Amazon CloudFront 宣布支持 IPv6 源站

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-cloudfront-ipv6-origins/](https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-cloudfront-ipv6-origins/) 

**发布时间:** 2025-09-08

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon CloudFront 宣布支持 IPv6 源站

发布于: 2025年9月8日

Amazon CloudFront 扩展了其 IPv6 功能，引入了对连接到源站 (origin servers) 的 IPv6 支持，允许客户为其 Web 应用程序实现端到端 (end-to-end) 的 IPv6 内容分发。对 IPv6 源站的支持使客户能够将 IPv6 流量一直发送到其源站，从而满足其在架构和法规上采用 IPv6 的要求。端到端的 IPv6 支持可以提升通过 IPv6 网络连接的最终用户的网络性能，并消除了对源站基础设施 IPv4 地址耗尽 (IPv4 address exhaustion) 的担忧。

此前，尽管 CloudFront 接受来自最终用户的 IPv6 连接，但仅支持与源站的 IPv4 连接。使用 CloudFront 的客户可以将其自定义源站 (custom origins) 配置为仅 IPv4 (默认)、仅 IPv6 或双栈 (dual-stack) 连接。使用双栈时，CloudFront 会自动在 IPv4 和 IPv6 地址之间进行选择，以确保流向源站的流量在两者之间均匀分布。

客户可以在所有支持的 AWS 商业区域 (AWS Commercial Regions) 中配置 IPv6 源站。客户可以为 CloudFront 配置仅 IPv6 或双栈源站，但不包括 Amazon S3 和 VPC 源站。要了解有关 CloudFront IPv6 支持的更多信息，请访问 [CloudFront 文档](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-enable-ipv6.html) 。

---

# AWS WAF 现根据请求量提供免费的 WAF Vended Logs

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/aws-waf-free-vended-logs-request-volume/](https://aws.amazon.com/about-aws/whats-new/2025/09/aws-waf-free-vended-logs-request-volume/) 

**发布时间:** 2025-09-08

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS WAF 现根据请求量提供免费的 WAF Vended Logs

发布于: 2025 年 9 月 8 日

AWS WAF 现在每处理 100 万次 WAF 请求，即可免费获得 500 MB 的 CloudWatch Logs Vended Logs (Vended Logs) 摄取量，无需额外付费。这有助于客户在保持全面安全可见性的同时，更好地管理其 WAF 日志记录成本。

CloudWatch 中的 WAF 日志为安全分析、合规性和故障排查提供了宝贵的洞察。客户可以利用 CloudWatch 的高级分析功能，包括 Log Insights 查询、异常检测 (anomaly detection) 和仪表板 (dashboards)，来监控和分析其 Web 应用程序的流量模式和安全事件。该免费日志配额会在月底根据您的 AWS 账单上的 WAF 请求使用量自动应用，使您能够轻松享受新的定价优惠。

此 WAF 免费日志配额适用于发送到 CloudWatch、S3 和 Firehose 的 WAF 特定 Vended Logs。每 100 万次 WAF 请求超出 500 MB 免费额度的使用量，将按照 CloudWatch 中 AWS WAF 特定的 Vended Logs 定价进行收费。有关定价详情，请访问 [AWS WAF 定价页面](https://aws.amazon.com/waf/pricing/) 。

要了解有关 WAF 日志记录功能的更多信息以及如何开始使用，请访问 [AWS WAF 文档](https://docs.aws.amazon.com/waf/latest/developerguide/logging-destinations.html) 。

---

# Amazon CloudFront 为签名 URL 新增 ECDSA 支持

发布于：2025 年 9 月 9 日

Amazon CloudFront 现已支持椭圆曲线数字签名算法 (Elliptic Curve Digital Signature Algorithm, ECDSA)，用于签名 URL (signed URLs) 和签名 Cookie (signed cookies)，为客户在内容访问控制方面提供了更强的性能和安全性。这一新增功能使客户可以根据其特定的安全和性能需求，在 RSA 和 ECDSA 加密算法之间灵活选择。
  
此前，CloudFront 仅支持基于 RSA 的加密算法来创建签名令牌 (signed tokens)。与传统的 RSA 签名相比，ECDSA 具有多项优势，包括更快的签名生成和验证速度、更小的签名尺寸 (从而缩短 URL 长度)，以及用更小的密钥长度实现同等的安全性。这使得 ECDSA 签名 URL 和签名 Cookie 特别适用于高流量应用、移动环境和物联网 (IoT) 设备等对处理效率和带宽优化至关重要的场景。
  
所有边缘站点 (edge locations) 均已支持通过签名 URL 和签名 Cookie 使用 ECDSA。此功能不包括由光环新网 (Sinnet) 运营的亚马逊云科技中国 (北京) 区域和由西云数据 (NWCD) 运营的亚马逊云科技中国 (宁夏) 区域。使用此功能无需额外付费。要了解有关限制通过 Amazon CloudFront 分发内容的更多信息，请访问 [CloudFront 文档。](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-signed-urls.html#private-content-how-signed-urls-work)

---

# Amazon EC2 C6in 实例现已在亚太地区 (泰国) 可用

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-ec2-c6in-instances-asia-pacific-thailand/](https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-ec2-c6in-instances-asia-pacific-thailand/) 

**发布时间:** 2025-09-10

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon EC2 C6in 实例现已在亚太地区 (泰国) 可用

发布于: 2025 年 9 月 10 日

即日起，Amazon Elastic Compute Cloud (Amazon EC2) C6in 实例已在 AWS 亚太地区 (泰国) 区域推出。这些第六代网络优化实例由第三代 Intel Xeon 可扩展处理器提供支持，并基于 [AWS Nitro 系统](https://aws.amazon.com/ec2/nitro/) 构建。它们提供高达 200Gbps 的网络带宽，是同类第五代实例网络带宽的 2 倍。

客户可以使用 C6in 实例来扩展各种应用的性能，例如网络虚拟设备 (防火墙、虚拟路由器、负载均衡器)、电信 5G 用户平面功能 (UPF)、数据分析、高性能计算 (HPC) 以及基于 CPU 的 AI/ML 工作负载。C6in 实例提供 10 种不同大小，最高可达 128 个 vCPU，并包含裸金属规格。Amazon EC2 第六代基于 x86 的网络优化 EC2 实例可提供高达 100Gbps 的 Amazon Elastic Block Store (Amazon EBS) 带宽和高达 400K IOPS。C6in 实例在 32xlarge 和 metal 规格上提供 Elastic Fabric Adapter (EFA) 网络支持。

C6in 实例已在以下 [AWS 区域](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 上线：美国东部 (俄亥俄、弗吉尼亚北部)、美国西部 (加利福尼亚北部、俄勒冈)、欧洲 (法兰克福、爱尔兰、伦敦、米兰、巴黎、西班牙、斯德哥尔摩、苏黎世)、中东 (巴林、阿联酋)、以色列 (特拉维夫)、亚太地区 (香港、海得拉巴、雅加达、马来西亚、墨尔本、孟买、大阪、首尔、新加坡、悉尼、东京、泰国)、非洲 (开普敦)、南美洲 (圣保罗)、加拿大 (中部)、加拿大西部 (卡尔加里) 以及 AWS GovCloud (美国西部、美国东部)。要了解更多信息，请访问 Amazon EC2 [C6in](https://aws.amazon.com/ec2/instance-types/c6i/) 实例页面。要开始使用，请访问 [AWS 管理控制台](https://console.aws.amazon.com/) 、[AWS 命令行界面 (AWS CLI)](https://aws.amazon.com/cli/) 和 [AWS SDKs](https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/EC2.html) 。

---

# AWS Elastic Beanstalk 现已支持应用程序负载均衡器和网络负载均衡器的双栈配置以启用 IPv6

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/aws-elastic-beanstalk-ipv6-dual-stack-configuration/](https://aws.amazon.com/about-aws/whats-new/2025/09/aws-elastic-beanstalk-ipv6-dual-stack-configuration/) 

**发布时间:** 2025-09-10

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Elastic Beanstalk 现已支持应用程序负载均衡器和网络负载均衡器的双栈配置以启用 IPv6

发布于: 2025 年 9 月 10 日

AWS Elastic Beanstalk 现已支持应用程序负载均衡器 (Application Load Balancers, ALB) 和网络负载均衡器 (Network Load Balancers, NLB) 的双栈配置 (dual-stack configuration)，允许环境同时服务于 IPv4 和 IPv6 协议。您现在可以将 `IpAddressType` 选项设置为 `dualstack`，Elastic Beanstalk 将自动为您的负载均衡器配置双栈支持，并创建 A 和 AAAA 两种 DNS 记录。您可以根据需要将现有的 IPv4 环境无缝升级到双栈，或回滚到原有配置。

这项功能可以帮助您在保持完全 IPv4 兼容性的同时，覆盖仅使用 IPv6 网络的用户，以满足全球可访问性要求和 IPv6 采用的强制规定。该功能会自动处理 DNS 记录管理，简化您应用程序的 IPv6 部署过程，并确保为所有用户提供最佳性能。

此功能已在所有支持 Elastic Beanstalk、应用程序负载均衡器和网络负载均衡器的 AWS 区域 (AWS regions) 上线。

有关详细的配置步骤，请参阅 [Elastic Beanstalk 开发人员指南](https://docs.aws.amazon.com/elastic-beanstalk/) 和 [负载均衡器文档](https://docs.aws.amazon.com/elasticloadbalancing/)。要了解有关 IPv6 网络的更多信息，请访问 [Amazon VPC 用户指南](https://docs.aws.amazon.com/vpc/)。

---

# Amazon Bedrock AgentCore Gateway 支持 AWS PrivateLink 调用和调用日志记录

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-bedrock-agentcore-gateway-privatelink-invocation-logging](https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-bedrock-agentcore-gateway-privatelink-invocation-logging) 

**发布时间:** 2025-09-10

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon Bedrock AgentCore Gateway 支持 AWS PrivateLink 调用和调用日志记录

发布于：2025 年 9 月 10 日

Amazon Bedrock AgentCore Gateway 现已支持通过 Amazon CloudWatch、Amazon S3 和 Amazon Data Firehose 进行 AWS PrivateLink 调用和调用日志记录 (invocation logging)。Amazon Bedrock AgentCore Gateway 为开发者提供了一种简单且安全的方式，用于大规模构建、部署、发现和连接代理工具 (agent tools)。借助 PrivateLink 支持和调用日志记录功能，您可以通过 AgentCore Gateway 对代理和工具应用网络和治理要求。

AWS PrivateLink 支持允许来自虚拟私有云 (VPC) 网络的用户和代理无需通过公共互联网即可访问 AgentCore Gateway。通过调用日志记录，您可以获得每个调用日志的可见性，并能深入排查问题或审计活动。

Amazon Bedrock AgentCore 目前处于预览阶段，已在美国东部 (弗吉尼亚北部)、美国西部 (俄勒冈)、亚太地区 (悉尼) 和欧洲 (法兰克福) 区域上线。要了解有关这些功能的更多信息，请参阅 [AWS 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) 。要了解有关 Amazon Bedrock AgentCore 及其服务的更多信息，请阅读 [新闻博客](https://aws.amazon.com/blogs/aws/introducing-amazon-bedrock-agentcore-securely-deploy-and-operate-ai-agents-at-any-scale/) 。

---

# Amazon CloudWatch Observability Access Manager 现已支持 VPC 端点

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-cloudwatch-observability-access-manager-vpc-endpoints/](https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-cloudwatch-observability-access-manager-vpc-endpoints/) 

**发布时间:** 2025-09-11

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon CloudWatch Observability Access Manager 现已支持 VPC 端点

发布于: 2025年9月11日

AWS 宣布 Amazon CloudWatch Observability Access Manager (OAM) 支持 VPC 端点 (VPC endpoints)。CloudWatch OAM 使您能够以编程方式管理区域内的跨账户可观测性设置。新的 VPC 端点通过将您的 VPC 和 CloudWatch OAM 之间的流量保留在 AWS 网络内，无需通过公共互联网传输，从而增强您的安全状况。

您可以使用 Observability Access Manager 在源账户和监控账户之间创建和管理链接，从而监控和排查跨区域内多个账户的应用程序。借助新的 VPC 端点，您可以在 VPC 和 CloudWatch Observability Access Manager 之间建立安全、私密且可靠的连接。这使您即使在没有互联网访问权限的 VPC 中，也能在管理跨账户可观测性链接和接收器 (sinks) 的同时保持私有连接。该功能支持 IPv4 和 IPv6 地址，您可以使用 AWS PrivateLink 的内置安全控制措施 (例如安全组和 VPC 端点策略) 来帮助保护对可观测性资源的访问。

CloudWatch Observability Access Manager VPC 端点现已在所有 [AWS 商业区域](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/) 、AWS GovCloud (US) 区域和中国区域推出。

要开始使用 CloudWatch Observability Access Manager 的 VPC 端点，请参阅 [CloudWatch OAM 端点](https://docs.aws.amazon.com/general/latest/gr/cloudwatchoam.html) 获取支持的区域端点列表。要了解有关 AWS PrivateLink 的更多信息，请参阅 [通过 AWS PrivateLink 访问 AWS 服务](https://docs.aws.amazon.com/vpc/latest/privatelink/privatelink-access-aws-services.html) 。

---

# 推出新的 EFA 指标，提升 AWS 网络的可观测性

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/aws-efa-metrics-improved-observability-networking](https://aws.amazon.com/about-aws/whats-new/2025/09/aws-efa-metrics-improved-observability-networking) 

**发布时间:** 2025-09-12

**厂商:** AWS

**类型:** WHATSNEW

---
# 推出新的 EFA 指标，提升 AWS 网络的可观测性

发布于：2025年9月12日

今天，AWS 推出了五项新的 Elastic Fabric Adapter (EFA) 指标，以增强人工智能/机器学习 (AI/ML) 和高性能计算 (HPC) 工作负载的网络可观测性。这些新指标通过跟踪重传数据包和字节、重传超时事件、远程连接受损事件以及远程接收器无响应事件，帮助诊断性能问题。

借助这些新指标，您可以监控网络拥塞或实例配置问题，从而及时采取措施来维持应用程序性能。这些指标在每个 EFA 设备级别上以计数器的形式实现，从实例启动或最近一次驱动程序重置开始累积数据。这些指标计数器存储在 sys 文件系统中，可通过实例命令行进行访问。为了增强监控和告警能力，您可以将这些指标集成到 Prometheus 脚本中，以便导出到 Grafana 等第三方工具，用于创建仪表板和设置告警。新指标适用于 Nitro v4 (及更高版本) 的实例，并要求 EFA 安装程序版本为 1.43.0 或更高。要获取完整的指标列表并了解如何使用它们，请访问 [监控 EFA](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-working-monitor.html) 用户指南。有关基于不同 Nitro 系统版本构建的实例的完整列表，请参阅 [AWS Nitro 系统文档](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-nitro-instances.html) 。

这些新指标已在所有商业 AWS 区域、AWS GovCloud (美国) 区域和中国区域提供支持。要了解有关 EFA 的更多信息，请访问 EFA [文档](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa.html) 。

---

# AWS Direct Connect 的虚拟接口现已支持 4 字节自治系统编号

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/aws-direct-connect-4-byte-autonomous-system-numbers/](https://aws.amazon.com/about-aws/whats-new/2025/09/aws-direct-connect-4-byte-autonomous-system-numbers/) 

**发布时间:** 2025-09-12

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Direct Connect 的虚拟接口现已支持 4 字节自治系统编号

发布于: 2025 年 9 月 12 日

AWS Direct Connect 现已为虚拟接口 (Virtual interfaces) 提供对 4 字节自治系统 (AS) 编号的支持。Direct Connect 使用标准的边界网关协议 (Border Gateway Protocol) 为客户提供到 AWS 全球网络的私有连接。然而，对于拥有复杂多租户网络拓扑或需要在整个网络中维护一致 AS 编号的客户而言，2 字节 AS 编号最多 65,536 个的限制可能会带来挑战。借助 4 字节 AS 编号，客户现在可以使用 RFC 6793 支持的完整范围，最高可达 4,294,967,294。
对 4 字节 AS 编号的支持现已在全球所有 AWS 区域以及所有 Direct Connect 虚拟接口类型上提供。要开始使用，请访问 AWS Direct Connect 控制台或使用更新后的 API 创建带有新 4 字节 AS 编号的虚拟接口。有关更多信息，请查阅 [AWS Direct Connect 文档](https://docs.aws.amazon.com/directconnect/latest/UserGuide/welcome.html) 。

---

# 宣布第二代 AWS Outposts 机架在新增的 52 个国家/地区推出
发布于: 2025 年 9 月 17 日

第二代 AWS Outposts 机架 (AWS Outposts racks) 现已可在澳大利亚、巴林、巴西、文莱、智利、哥斯达黎加、埃及、欧盟国家、冰岛、印度尼西亚、以色列、日本、约旦、肯尼亚、沙特阿拉伯王国、科威特、马来西亚、新西兰、秘鲁、菲律宾、新加坡、特立尼达和多巴哥、土耳其、阿拉伯联合酋长国 (UAE)、英国和越南的数据中心 (data center) 和本地位置进行运送和安装。

Outposts 机架可将 AWS 基础设施、AWS 服务、API 和工具扩展到几乎任何本地数据中心或托管空间，以提供真正一致的混合体验 (hybrid experience)。Outposts 机架非常适合需要低延迟 (low-latency) 访问本地系统、进行本地数据处理 (local data processing) 以及迁移具有本地系统相互依赖关系的应用程序的工作负载 (workloads)。Outposts 机架还有助于满足数据驻留 (data residency) 的要求。第二代 Outposts 机架支持最新一代由 x86 驱动的 Amazon Elastic Compute Cloud (Amazon EC2) 实例 (instances)，首先推出的是 C7i、M7i 和 R7i 实例。与第一代 Outposts 机架上的 C5、M5 和 R5 实例相比，这些实例的性能提升高达 40%。第二代 Outposts 机架还提供简化的网络扩展和配置，并支持一类专为超低延迟和高吞吐量需求而优化的新型加速网络 (accelerated networking) Amazon EC2 实例。

随着第二代 Outposts 机架在上述国家/地区的推出，您可以使用 AWS 服务在您本国的本地设施中运行工作负载和数据，并连接到最近的可用 AWS 区域 (AWS Region) 进行管理和运营。

要了解有关第二代 Outposts 机架的更多信息，请阅读[这篇博文](https://aws.amazon.com/blogs/aws/announcing-second-generation-aws-outposts-racks-with-breakthrough-performance-and-scalability-on-premises/) 和[用户指南](https://docs.aws.amazon.com/outposts/latest/network-userguide/what-is-outposts.html) 。有关支持第二代 Outposts 机架的国家/地区和 AWS 区域的最新列表，请查看 [Outposts 机架常见问题解答页面](https://aws.amazon.com/outposts/rack/faqs/) 。

---

# Amazon VPC 可达性分析器和 Amazon VPC 网络访问分析器现已在七个新增的 AWS 区域可用

**发布于:** 2025年9月18日

---
随着本次发布，Amazon VPC 可达性分析器 (Amazon VPC Reachability Analyzer) 和 Amazon VPC 网络访问分析器 (Amazon VPC Network Access Analyzer) 现已在亚太地区 (新西兰)、亚太地区 (海得拉巴)、亚太地区 (墨尔本)、亚太地区 (台北)、加拿大西部 (卡尔加里)、以色列 (特拉维夫) 和墨西哥 (中部) 区域可用。

VPC 可达性分析器通过分析您的网络配置，帮助您诊断虚拟私有云 (VPCs) 中源资源与目标资源之间的网络可达性。例如，可达性分析器可以帮助您识别 VPC 路由表中缺失的路由条目，该问题可能导致您 AWS Organization 中账户 A 的一个 EC2 实例无法连接到账户 B 的另一个 EC2 实例。

VPC 网络访问分析器可以帮助您识别对 AWS 资源的意外网络访问，从而协助您满足安全与合规性要求。例如，您可以创建一个范围来验证从您的 Web 应用程序到互联网的所有路径都经过防火墙，并检测任何绕过防火墙的路径。

要了解更多信息，请访问 [VPC 可达性分析器](https://docs.aws.amazon.com/vpc/latest/reachability/what-is-reachability-analyzer.html) 和 [VPC 网络访问分析器](https://docs.aws.amazon.com/vpc/latest/network-access-analyzer/what-is-network-access-analyzer.html) 的文档。有关定价信息，请参阅 [Amazon VPC 定价页面](https://aws.amazon.com/vpc/pricing/) 上的“网络分析”选项卡。

---

# 第二代 AWS Outposts 机架现已在 AWS 加拿大 (中部) 和美国西部 (北加州) 区域提供支持

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/second-generation-outposts-racks-canada-us-west-regions](https://aws.amazon.com/about-aws/whats-new/2025/09/second-generation-outposts-racks-canada-us-west-regions) 

**发布时间:** 2025-09-18

**厂商:** AWS

**类型:** WHATSNEW

---
# 第二代 AWS Outposts 机架现已在 AWS 加拿大 (中部) 和美国西部 (北加州) 区域提供支持

发布于: 2025 年 9 月 18 日

第二代 AWS Outposts 机架 (Second-generation AWS Outposts racks) 现已在 AWS 加拿大 (中部) 和美国西部 (北加州) 区域提供支持。Outposts 机架将 AWS 基础设施、AWS 服务、API 和工具扩展到几乎任何本地数据中心 (on-premises data center) 或主机托管空间 (colocation space)，以提供真正一致的混合体验 (hybrid experience)。

从初创公司到大型企业，再到公共部门，加拿大和美国内外的各类组织现在都可以订购连接到这两个新增支持区域的 Outposts 机架，以优化其延迟和数据驻留 (data residency) 需求。Outposts 允许客户在本地运行需要低延迟访问本地系统的工作负载，同时连接回其主区域进行应用程序管理。客户还可以使用 Outposts 和 AWS 服务来管理和处理需要保留在本地以满足数据驻留要求的数据。此次区域扩展为客户的 Outposts 可连接的 AWS 区域提供了更大的灵活性。

要了解有关第二代 Outposts 机架的更多信息，请阅读 [*这篇博客文章*](https://aws.amazon.com/blogs/aws/announcing-second-generation-aws-outposts-racks-with-breakthrough-performance-and-scalability-on-premises/) 和 [*用户指南*](https://docs.aws.amazon.com/outposts/latest/network-userguide/what-is-outposts.html) 。有关支持第二代 Outposts 机架的国家和地区以及 AWS 区域的最新列表，请查看 [*Outposts 机架常见问题页面*](https://aws.amazon.com/outposts/rack/faqs/) 。

---

# Application Recovery Controller 的区域切换功能现已在亚太 (新西兰) 区域推出

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/application-recovery-controller-region-switch-new-zealand/](https://aws.amazon.com/about-aws/whats-new/2025/09/application-recovery-controller-region-switch-new-zealand/) 

**发布时间:** 2025-09-24

**厂商:** AWS

**类型:** WHATSNEW

---
# Application Recovery Controller 的区域切换功能现已在亚太 (新西兰) 区域推出

发布于: 2025 年 9 月 24 日

Amazon Application Recovery Controller (ARC) 中的区域切换 (Region switch) 功能现已在亚太 (新西兰) 区域推出。区域切换功能允许您编排具体步骤，以便将跨 AWS 账户的应用程序资源切换到另一个 AWS 区域运行。它提供仪表板，用于实时了解恢复过程，并从各类资源和账户中收集向监管机构和合规团队报告所需的数据。对于主/备 (active/passive) 多区域架构，区域切换支持故障切换 (failover) 和故障恢复 (failback)；对于双活 (active/active) 多区域架构，则支持转移 (shift-away) 和返回 (return)。当您创建区域切换计划时，该计划会被复制到您应用程序运行的所有区域。这消除了恢复操作对您正在迁离的区域的依赖关系。

要开始使用，您可以通过 ARC 控制台、API 或 CLI 构建一个区域切换计划。要了解更多信息，请访问 [ARC 区域切换文档](https://docs.aws.amazon.com/r53recovery/latest/dg/region-switch.html) 和 [定价页面](https://aws.amazon.com/application-recovery-controller/pricing/)。

---

# Amazon Route 53 Resolver 查询日志功能现已在亚太地区 (新西兰) 可用

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-route-53-resolver-query-logging-available-asia-pacific-nz](https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-route-53-resolver-query-logging-available-asia-pacific-nz) 

**发布时间:** 2025-09-24

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon Route 53 Resolver 查询日志功能现已在亚太地区 (新西兰) 可用

发布于: 2025 年 9 月 24 日

今天，我们宣布 Route 53 Resolver 查询日志功能现已在亚太地区 (新西兰) 推出，使您能够记录源自 Amazon Virtual Private Cloud (Amazon VPC) 的 DNS 查询。启用查询日志后，您可以看到查询了哪些域名、查询源自哪些 AWS 资源 (包括源 IP 和实例 ID) 以及收到的响应。

Route 53 Resolver 是 Amazon 提供的 DNS 服务器，默认在所有 Amazon VPC 中可用。Route 53 Resolver 响应来自 VPC 内 AWS 资源的 DNS 查询，这些查询涉及公有 DNS 记录、Amazon VPC 特定的 DNS 名称以及 Amazon Route 53 私有托管区域 (private hosted zones)。借助 Route 53 Resolver 查询日志功能，客户可以记录源自其 VPC 内部的 DNS 查询和响应，无论这些查询是由 Route 53 Resolver 在本地应答、通过公共互联网解析，还是通过 [解析器终端节点 (Resolver Endpoints)](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html) 转发到本地 DNS 服务器。您可以使用 [AWS Resource Access Manager (RAM)](https://aws.amazon.com/ram/) 在多个账户之间共享您的查询日志配置。您还可以选择将查询日志发送到 Amazon S3、Amazon CloudWatch Logs 或 Amazon Data Firehose。

使用 Route 53 Resolver 查询日志功能无需额外付费，但您可能会产生来自 Amazon S3、Amazon CloudWatch 或 Amazon Data Firehose 的使用费。要了解有关 Route 53 Resolver 查询日志的更多信息或开始使用，请访问 [Route 53 Resolver 产品页面](https://aws.amazon.com/route53/resolver/) 或 [Route 53 文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-query-logs.html) 。

---

# AWS Network Firewall 增强应用层流量控制

发布于：2025 年 9 月 25 日

[AWS Network Firewall](https://aws.amazon.com/network-firewall/) 是一项托管服务 (managed service)，可以轻松地为您的 Amazon VPC 部署必要的网络保护。该服务现在提供了增强的默认规则，用于处理 TLS 客户端 Hello 消息 (TLS client hellos) 以及跨多个数据包拆分的 HTTP 请求。本次更新引入了新的应用层默认有状态操作，即“丢弃” (drop) 和“对已建立连接告警” (alert established)，使客户能够在支持现代 TLS 实现和大型 HTTP 请求的同时，维持安全控制。

这些增强功能帮助客户无需编写复杂的自定义规则，即可实施强大的安全策略。现在，当关键信息分段到多个数据包中时，安全团队可以有效地检查和筛选这些流量，同时通过详细的日志记录选项保持可见性，从而更轻松地使用现代协议和加密标准来保护应用程序。

该功能已在支持 AWS Network Firewall 的所有 AWS 区域 (AWS Regions) 提供。

要了解更多信息，请参阅 AWS Network Firewall 服务 [文档](https://docs.aws.amazon.com/network-firewall/)。

---

# AWS Direct Connect 宣布在西班牙马德里设立新站点

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/aws-direct-connect-madrid-mad3/](https://aws.amazon.com/about-aws/whats-new/2025/09/aws-direct-connect-madrid-mad3/) 

**发布时间:** 2025-09-30

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Direct Connect 宣布在西班牙马德里设立新站点

发布于：2025 年 9 月 30 日

今天，AWS 宣布在西班牙马德里附近的 Digital Realty MAD3 数据中心内启用一个新的 [AWS Direct Connect](https://aws.amazon.com/directconnect) 站点。现在，您可以通过该站点建立到所有公共 AWS 区域 (中国区域除外)、AWS GovCloud 区域和 [AWS 本地扩展区域 (AWS Local Zones)](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) 的私有、直接网络访问。这是马德里的第三个站点，也是西班牙境内的第四个 AWS Direct Connect 站点。该 Direct Connect 站点提供专用的 10 Gbps 和 100 Gbps 连接，并支持 MACsec 加密。

Direct Connect 服务使您能够在 AWS 与您的数据中心、办公室或主机托管环境之间建立私有的物理网络连接。与通过公共互联网建立的连接相比，这些私有连接可以提供更一致的网络体验。

有关全球超过 146 个 Direct Connect 站点的更多信息，请访问 Direct Connect [产品详情页面](https://aws.amazon.com/directconnect) 的 [站点](https://aws.amazon.com/directconnect/locations/) 部分。或者，访问我们的 [入门](https://aws.amazon.com/directconnect/getting-started/) 页面，了解有关如何购买和部署 Direct Connect 的更多信息。

---

# AWS Direct Connect 宣布在哥伦比亚波哥大扩展 100G 连接

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/09/aws-direct-connect-100g-expansion-bogota/](https://aws.amazon.com/about-aws/whats-new/2025/09/aws-direct-connect-100g-expansion-bogota/) 

**发布时间:** 2025-09-30

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Direct Connect 宣布在哥伦比亚波哥大扩展 100G 连接

发布于: 2025 年 9 月 30 日

今天，AWS 宣布在位于哥伦比亚波哥大附近的 Equinix BG1 数据中心的现有 [AWS Direct Connect](https://aws.amazon.com/directconnect) 站点，扩展了具备 MACsec 加密 (MACsec encryption) 功能的 10 Gbps 和 100 Gbps 专用连接。您现在可以从该站点建立私有的直接网络访问，连接到所有公共 AWS 区域 (中国区除外)、AWS GovCloud 区域以及 [AWS 本地扩展区域 (AWS Local Zones)](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) 。

Direct Connect 服务使您能够在 AWS 与您的数据中心、办公室或主机托管环境 (colocation environment) 之间建立私有的物理网络连接。与通过公共互联网建立的连接相比，这些私有连接可以提供更一致的网络体验。

要了解有关全球超过 146 个 Direct Connect 站点的更多信息，请访问 Direct Connect [产品详情页面](https://aws.amazon.com/directconnect) 中的 [站点](https://aws.amazon.com/directconnect/locations/) 部分。或者，访问我们的 [入门](https://aws.amazon.com/directconnect/getting-started/) 页面，了解如何购买和部署 Direct Connect。

---

# AWS Cloud WAN 现已在 AWS GovCloud (US) 区域推出

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/10/aws-cloud-wan-govcloud/](https://aws.amazon.com/about-aws/whats-new/2025/10/aws-cloud-wan-govcloud/) 

**发布时间:** 2025-10-01

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Cloud WAN 现已在 AWS GovCloud (US) 区域推出

发布于: 2025年10月1日

自今日起，[AWS Cloud WAN](https://aws.amazon.com/cloud-wan/) 现已在 AWS GovCloud (US-West) 和 AWS GovCloud (US-East) 区域推出。

借助 AWS Cloud WAN，您可以使用一个中央控制面板和网络策略来创建一个跨越多个位置和网络的全球网络，从而无需再使用不同技术来配置和管理不同的网络。您可以使用网络策略来指定希望通过 AWS Site-to-Site VPN、AWS Direct Connect 或第三方软件定义广域网 (SD-WAN) 产品连接的 Amazon Virtual Private Clouds (VPC)、AWS Transit Gateways 和本地位置。AWS Cloud WAN 中央控制面板会生成网络的全面视图，以帮助您监控网络的运行状况、安全性和性能。此外，AWS Cloud WAN 通过使用边界网关协议 (BGP) 自动创建跨 AWS 区域的全球网络，以便您可以在全球范围内轻松交换路由。

要了解更多信息，请访问 AWS Cloud WAN [产品详情页面](https://aws.amazon.com/cloud-wan/)。

---

# AWS Direct Connect 宣布在菲律宾马卡蒂市扩展 100G 连接

发布于：2025 年 10 月 2 日

今天，AWS 宣布在位于菲律宾马卡蒂市附近的 ePLDT 数据中心内的现有 [AWS Direct Connect](https://aws.amazon.com/directconnect) 站点，扩展了具备 MACsec 加密功能的 10 Gbps 和 100 Gbps 专用连接。您现在可以从该站点建立到所有公共 AWS 区域 (中国区除外)、AWS GovCloud 区域和 [AWS 本地扩展区域 (Local Zones)](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) 的私有直接网络访问。

Direct Connect 服务使您能够建立 AWS 与您的数据中心、办公室或主机托管环境之间的私有物理网络连接。与通过公共互联网建立的连接相比，这些私有连接可以提供更一致的网络体验。

有关全球超过 146 个 Direct Connect 站点的更多信息，请访问 Direct Connect [产品详情页面](https://aws.amazon.com/directconnect) 的 [站点](https://aws.amazon.com/directconnect/locations/) 部分。或者，访问我们的 [入门](https://aws.amazon.com/directconnect/getting-started/) 页面，以了解有关如何购买和部署 Direct Connect 的更多信息。

---

# Amazon VPC Lattice 现已支持为资源网关配置 IP 地址

发布于: 2025 年 10 月 7 日

即日起，Amazon VPC Lattice 允许您为资源网关 (Resource Gateway) 的弹性网络接口 (ENIs) 配置分配的 IPv4 地址数量。这项增强功能建立在 VPC Lattice 的现有能力之上，即跨多个 VPC 和账户提供对第 4 层 (Layer-4) 资源的访问，例如数据库、集群、域名等。

在配置资源网关时，您现在可以为每个 ENI 指定 IPv4 地址的数量，该设置一旦配置便不可更改。这些 IPv4 地址用于网络地址转换 (Network Address Translation)，并决定了到单个资源的最大并发 IPv4 连接数。在配置 IPv4 地址数量时，您应充分考虑预期的连接量。默认情况下，VPC Lattice 会为每个 ENI 分配 16 个 IPv4 地址。对于 IPv6，VPC Lattice 始终为每个 ENI 分配一个 /80 CIDR。

此功能已在所有提供 VPC Lattice 的 AWS 区域 (AWS Regions) 推出，无需额外费用。要了解更多信息，请访问 [Amazon VPC Lattice 产品详情页面](https://aws.amazon.com/vpc/lattice/) 和 [Amazon VPC Lattice 文档](https://docs.aws.amazon.com/vpc-lattice/latest/ug/resource-gateway.html#ipv4-address-type-per-eni)。

---

# Amazon DynamoDB 现已支持互联网协议第 6 版 (IPv6)
发布于: 2025 年 10 月 9 日

[Amazon DynamoDB](https://aws.amazon.com/dynamodb/)  现已为客户提供在 Amazon Virtual Private Cloud (VPC)  中使用互联网协议第 6 版 (IPv6)  地址的选项，用于连接到 DynamoDB 表、流和 DynamoDB Accelerator (DAX)，包括通过 AWS PrivateLink 网关和接口终端节点 (Interface endpoints)  进行连接。迁移到 IPv6 的客户可以通过使用同时支持 IPv4 和 IPv6 的网络来简化其网络堆栈 (network stack)  并满足合规性要求。

互联网的持续发展正在耗尽可用的互联网协议第 4 版 (IPv4)  地址。IPv6 将可用地址数量增加了几个数量级，客户不再需要在其 VPC 中管理重叠的地址空间 (address spaces)。客户只需在 AWS 管理控制台 (AWS Management Console)  中点击几下，即可迁移到 IPv6，从而将其应用程序标准化到新版本的互联网协议上。

Amazon DynamoDB 对 IPv6 的支持现已在美国所有 AWS 商业区域 (commercial AWS Regions)  和 AWS GovCloud (US) 区域上线。未来几周内，该功能将部署到 Amazon DynamoDB 可用的其余全球 AWS 区域。

要使用 IPv6 地址连接到 DynamoDB 并查看区域可用性，请参阅 [DynamoDB 开发人员指南](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/AccessingDynamoDB.html#dual-stackipv4-6)  和 [DynamoDB Accelerator 用户指南](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DAX.create-cluster.DAX_and_IPV6.html)。

---

# Amazon EC2 M6in 和 M6idn 实例现已在亚太地区 (首尔) 区域推出

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-ec2-m6in-m6idn-asia-pacific-seoul/](https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-ec2-m6in-m6idn-asia-pacific-seoul/) 

**发布时间:** 2025-10-09

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon EC2 M6in 和 M6idn 实例现已在亚太地区 (首尔) 区域推出

发布于: 2025年10月9日

即日起，[Amazon Elastic Compute Cloud (Amazon EC2) M6in 和 M6idn 实例](https://aws.amazon.com/ec2/instance-types/m6i) 现已在 AWS 亚太地区 (首尔) 区域推出。这些第六代网络优化实例基于第三代 Intel Xeon Scalable 处理器和 [AWS Nitro System](https://aws.amazon.com/ec2/nitro/) 构建，可提供高达 200Gbps 的网络带宽，是同类第五代实例网络带宽的两倍。客户可以使用 M6in 和 M6idn 实例来扩展网络密集型工作负载的性能和吞吐量，例如高性能文件系统、分布式 Web 规模内存缓存、缓存队列、实时大数据分析以及 5G 用户平面功能 (User Plane Function) 等电信应用。

M6in 和 M6idn 实例提供 10 种不同的实例规格，包括裸金属 (metal) 规格，最高可提供 128 个 vCPU 和 512 GiB 内存。它们提供高达 100Gbps 的 [Amazon Elastic Block Store (EBS)](https://aws.amazon.com/ebs/) 带宽和高达 400K IOPS。M6in 和 M6idn 实例的 32xlarge 和裸金属规格支持 [Elastic Fabric Adapter (EFA)](https://aws.amazon.com/hpc/efa/) 网络。M6idn 实例提供高达 7.6 TB 的高速、低延迟实例存储。

随着此次区域扩展，M6in 和 M6idn 实例现已在以下 AWS 区域推出：美国东部 (俄亥俄、弗吉尼亚北部)、美国西部 (北加利福尼亚、俄勒冈)、欧洲 (爱尔兰、法兰克福、西班牙、斯德哥尔摩、苏黎世)、亚太地区 (孟买、新加坡、东京、悉尼、首尔)、加拿大 (中部) 以及 AWS GovCloud (美国西部)。客户可以通过 Savings Plans、按需实例 (On-Demand) 和竞价实例 (Spot instances) 购买这些新实例。要了解更多信息，请访问 [M6in 和 M6idn 实例页面](https://aws.amazon.com/ec2/instance-types/m6i/)。

---

# AWS Direct Connect 宣布在密苏里州堪萨斯城扩展 100G 连接

发布于：2025 年 10 月 9 日

今天，AWS 宣布在位于密苏里州堪萨斯城附近的 Netrality KC1 数据中心的现有 [AWS Direct Connect](https://aws.amazon.com/directconnect) 站点，扩展了具备 MACsec 加密 (MACsec encryption) 功能的 10 Gbps 和 100 Gbps 专用连接。您现在可以从该站点建立到所有公共 AWS 区域 (AWS Regions) (中国区域除外)、AWS GovCloud 区域 (AWS GovCloud Regions) 和 [AWS 本地扩展区域 (AWS Local Zones)](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) 的私有直接网络访问。

Direct Connect 服务使您能够在 AWS 与您的数据中心、办公室或托管环境 (colocation environment) 之间建立私有的物理网络连接。与通过公共互联网建立的连接相比，这些私有连接可以提供更一致的网络体验。

有关全球超过 146 个 Direct Connect 站点的更多信息，请访问 Direct Connect [产品详情页面](https://aws.amazon.com/directconnect) 的 [站点](https://aws.amazon.com/directconnect/locations/) 部分。或者，访问我们的 [入门](https://aws.amazon.com/directconnect/getting-started/) 页面，了解有关如何购买和部署 Direct Connect 的更多信息。

---

# AWS Client VPN 现已支持 MacOS Tahoe

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/10/aws-client-vpn-macos-tahoe/](https://aws.amazon.com/about-aws/whats-new/2025/10/aws-client-vpn-macos-tahoe/) 

**发布时间:** 2025-10-10

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Client VPN 现已支持 MacOS Tahoe

发布于: 2025-10-10

AWS Client VPN 现已通过 5.3.1 版本支持 MacOS Tahoe 客户端。您现在可以在最新的 MacOS 版本上运行 AWS 提供的 VPN 客户端。AWS Client VPN 桌面客户端可免费使用，并可从[此处](https://aws.amazon.com/vpn/client-vpn-download/) 下载。

AWS Client VPN 是一项托管服务 (managed service)，可将您的远程办公人员安全地连接到 AWS 或 on-premises 网络。它支持适用于 MacOS、Windows x64、Windows Arm64 和 Ubuntu-Linux 的桌面客户端。从 5.3.1 版本开始，Client VPN 现已支持 MacOS Tahoe 26.0。它已经支持 Mac OS 13.0、14.0 和 15.0 版本，Windows 10 (x64) 和 Windows 11 (Arm64 和 x64)，以及 Ubuntu Linux 22.04 和 24.04 LTS 版本。

要了解有关 Client VPN 的更多信息：

- 访问 AWS Client VPN [产品页面](https://aws.amazon.com/vpn/) 
- 阅读 AWS Client VPN [文档](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/what-is.html) 
- 阅读 AWS Client VPN [用户指南](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/client-vpn-user-what-is.html)

---

# Amazon Route 53 Profiles 现已支持 AWS PrivateLink

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-route-53-profiles-supports-aws-privatelink](https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-route-53-profiles-supports-aws-privatelink) 

**发布时间:** 2025-10-14

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon Route 53 Profiles 现已支持 AWS PrivateLink

发布于: 2025年10月14日

Amazon Route 53 Profiles 现已支持 [AWS PrivateLink](https://aws.amazon.com/privatelink/) 。客户现在可以私密地访问和管理其 Profiles，无需通过公共互联网。AWS PrivateLink 在 Amazon 网络上安全地为 VPC、AWS 服务和本地应用程序 (on-premises applications) 之间提供私有连接。当通过 AWS PrivateLink 访问 Route 53 Profiles 时，所有操作 (例如创建、删除、编辑和列出 Profiles) 都可以通过 Amazon 私有网络处理。

Route 53 Profiles 允许您以 Profile 的形式定义标准 DNS 配置，其中可包含 Route 53 私有托管区域 (private hosted zone, PHZ) 关联、Route 53 Resolver 规则以及 Route 53 Resolver DNS Firewall 规则组，并将此配置应用于您账户中的多个 VPC。Profiles 还可用于为您的 VPC 强制执行 DNS 设置，包括 DNSSEC 验证、Resolver 反向 DNS 查找以及 DNS Firewall 故障模式 (failure mode) 的配置。您可以使用 AWS Resource Access Manager (RAM) 与您组织中的 AWS 账户共享 Profiles。在 Route 53 Profiles 当前可用的区域，包括 AWS GovCloud (US) 区域，客户可以将 Profiles 与 AWS PrivateLink 结合使用。有关 Profiles 可用 AWS 区域的更多信息，请参阅 [此文档](https://docs.aws.amazon.com/general/latest/gr/r53.html) 。

要了解有关配置 Route 53 Profiles 的更多信息，请参阅该服务的 [文档](https://docs.aws.amazon.com/Route53/latest/APIReference/API_Operations_Route_53_Profiles.html) 。

---

# AWS Application Load Balancer 推出 URL 和主机标头重写功能

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/10/application-load-balancer-url-header-rewrite](https://aws.amazon.com/about-aws/whats-new/2025/10/application-load-balancer-url-header-rewrite)

**发布时间:** 2025-10-15

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Application Load Balancer 推出 URL 和主机标头重写功能

发布于: 2025 年 10 月 15 日

Amazon Web Services (AWS) 宣布为应用程序负载均衡器 (Application Load Balancer, ALB) 推出 URL 和主机标头 (Host Header) 重写功能。该功能允许客户在将请求路由到目标之前，使用基于正则表达式 (regex) 的模式匹配来修改请求的 URL 和主机标头。

通过 URL 和主机标头重写，您可以使用正则表达式模式转换 URL (例如，将 “/api/v1/users” 重写为 “/users”)、在不同应用程序之间标准化 URL 模式、修改用于内部服务路由的主机标头、删除或添加 URL 路径前缀，以及将旧的 URL 结构重定向到新格式。这项功能无需额外的代理层，从而简化了应用程序架构。该功能对于微服务 (microservices) 部署非常有价值，因为在这种场景下，维持单一外部主机名同时路由到不同内部服务至关重要。

您可以通过 AWS 管理控制台 (AWS Management Console)、AWS CLI、AWS SDK 和 AWS API 配置 URL 和主机标头重写。使用 URL 和主机标头重写功能不收取额外费用。您只需根据 Application Load Balancer 的定价支付使用费用。

该功能现已在所有 AWS 商业区域推出。

要了解更多信息，请访问关于 Application Load Balancer 的 URL 和主机标头重写的 [ALB 文档](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/rule-transforms.html) 和 [AWS 博客文章](https://aws.amazon.com/blogs/networking-and-content-delivery/introducing-url-and-host-header-rewrite-with-aws-application-load-balancers) 。

---

# AWS Global Accelerator 现已在另外两个 AWS 区域支持终端节点

发布于: 2025-10-16

---
# AWS Global Accelerator 现已在另外两个 AWS 区域支持终端节点

自今日起，[AWS Global Accelerator](https://aws.amazon.com/global-accelerator/) 开始在另外两个 AWS 区域——亚太地区 (泰国) 区域和亚太地区 (台北) 区域——支持应用程序终端节点，从而将 [支持的 AWS 区域](https://docs.aws.amazon.com/global-accelerator/latest/dg/preserve-client-ip-address.regions.html) 数量扩展至三十三个。

AWS Global Accelerator 是一项旨在提高面向互联网的应用程序的可用性 (availability)、安全性和性能 (performance) 的服务。通过使用无拥塞的 AWS 网络，访问您应用程序的最终用户流量将受益于更高的可用性、边缘的 DDoS 防护以及相较于公共互联网更高的性能。Global Accelerator 提供静态 IP 地址 (static IP addresses)，作为您在一个或多个 AWS 区域中应用程序资源 (如 Application Load Balancer、Network Load Balancer、Amazon EC2 实例或 Elastic IP) 的固定入口终端节点。Global Accelerator 会持续监控您应用程序终端节点的运行状况，并为多区域工作负载 (multi-region workloads) 提供无需任何 DNS 依赖的确定性故障转移 (deterministic fail-over)。

要开始使用，请访问 AWS Global Accelerator [网站](https://aws.amazon.com/global-accelerator/) 并查阅其 [文档](https://docs.aws.amazon.com/global-accelerator/index.html) 。

---

# AWS RTB Fabric 正式可用：专为实时竞价工作负载打造

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/10/aws-rtb-fabric-generally-available/](https://aws.amazon.com/about-aws/whats-new/2025/10/aws-rtb-fabric-generally-available/) 

**发布时间:** 2025-10-23

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS RTB Fabric 正式可用：专为实时竞价工作负载打造

发布于: 2025年10月23日

今天，AWS 宣布推出 RTB Fabric，这是一项完全托管服务 (fully managed service)，可帮助您通过私有、高性能的网络环境，以个位数毫秒级延迟连接到您的广告技术 (AdTech) 合作伙伴，例如 Amazon Ads、GumGum、Kargo、MobileFuse、Sovrn、TripleLift、Viant、Yieldmo 等，整个过程仅需三个步骤。RTB Fabric 可将标准云网络成本降低高达 80%，且无需预先承诺。

该服务包含模块 (modules) 功能，可帮助您将自己的应用和合作伙伴的应用安全地引入计算环境，用于实时竞价 (real-time bidding)。模块支持容器化应用和基础模型 (FMs)，可增强交易效率和竞价效果。目前，AWS RTB Fabric 推出了三个内置模块，帮助您优化流量、提高竞价效率并增加出价响应率——所有模块均内联运行，以实现一致的低延迟执行。AWS RTB Fabric 帮助您优化竞拍执行、最大化供应方变现并增加发布商收入。您可以更快地与广告技术公司建立连接，以触达目标受众、扩大营销活动规模并提高性能，从而获得更高的广告支出回报率。

AWS RTB Fabric 已在以下 [AWS 区域 (Regions)](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 正式可用：美国东部 (弗吉尼亚北部)、美国西部 (俄勒冈)、亚太地区 (新加坡)、亚太地区 (东京)、欧洲 (法兰克福) 和欧洲 (爱尔兰)。要了解更多信息，请阅读[博客文章](https://aws.amazon.com/blogs/aws/introducing-aws-rtb-fabric-for-real-time-advertising-technology-workloads) 、[文档](https://docs.aws.amazon.com/rtb-fabric/latest/userguide/what-is-rtb-fabric.html) 或访问 [AWS RTB Fabric 产品页面](https://aws.amazon.com/rtb-fabric/) 。

---

# Amazon VPC 可达性分析器和 Amazon VPC 网络访问分析器现已在 AWS GovCloud (美国) 区域推出

发布于: 2025年10月24日

随着本次发布，Amazon [VPC 可达性分析器 (VPC Reachability Analyzer)](https://docs.aws.amazon.com/vpc/latest/reachability/getting-started.html) 和 Amazon VPC [网络访问分析器 (Network Access Analyzer)](https://docs.aws.amazon.com/vpc/latest/network-access-analyzer/what-is-network-access-analyzer.html) 现已在 AWS GovCloud (US-West) 和 AWS GovCloud (US-East) 区域推出。

VPC 可达性分析器通过分析您的网络配置，可以诊断您在虚拟私有云 (VPC) 中源资源与目标资源之间的网络可达性。例如，可达性分析器可以帮助您识别 VPC 路由表 (route table) 中缺失的路由表条目，该条目可能阻塞了您 AWS Organization 中账户 A 的一个 EC2 实例与账户 B 的另一个 EC2 实例之间的网络可达性。

VPC 网络访问分析器可以帮助您识别对 AWS 资源的意外网络访问，从而满足您的安全与合规性准则。例如，您可以创建一个范围 (scope) 来验证从您的 Web 应用程序到互联网的所有路径都经过防火墙 (firewall)，并检测任何绕过防火墙的路径。

要了解更多信息，请访问 [VPC 可达性分析器](https://docs.aws.amazon.com/vpc/latest/reachability/what-is-reachability-analyzer.html) 和 [VPC 网络访问分析器](https://docs.aws.amazon.com/vpc/latest/network-access-analyzer/what-is-network-access-analyzer.html) 的文档。有关定价信息，请参阅 [Amazon VPC 定价页面](https://aws.amazon.com/vpc/pricing/) 上的“网络分析”选项卡。

---

# 为 AI、ML 和 HPC 实例类型推出容量预留拓扑 API (Capacity Reservation Topology API)

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/10/capacity-reservation-topology-api-ai-ml-hpc-instance-type](https://aws.amazon.com/about-aws/whats-new/2025/10/capacity-reservation-topology-api-ai-ml-hpc-instance-type) 

**发布时间:** 2025-10-30

**厂商:** AWS

**类型:** WHATSNEW

---
# 为 AI、ML 和 HPC 实例类型推出容量预留拓扑 API (Capacity Reservation Topology API)

发布于: 2025年10月30日

AWS 宣布正式发布 Amazon Elastic Compute Cloud (EC2) 的容量预留拓扑 API (Capacity Reservation Topology API)。该 API 与实例拓扑 API (Instance Topology API) 相结合，使客户能够为人工智能 (Artificial Intelligence)、机器学习 (Machine Learning) 和高性能计算 (High-Performance Computing) 的分布式工作负载高效地管理容量、调度作业和对节点进行排序。容量预留拓扑 API 为客户提供了其容量预留相对位置的、每个账户专属的分层视图。

运行分布式并行工作负载的客户通常需要管理分布在数十到数百个容量预留中的数千个实例。借助容量预留拓扑 API，客户可以将其预留的拓扑描述为一个网络节点集，从而在无需启动实例的情况下，展示其容量的相对邻近度。这使得客户在紧密耦合的容量上配置工作负载时，能够进行高效的容量规划和管理。然后，客户可以使用实例拓扑 API，该 API 在容量预留拓扑 API 的基础上提供了一致的网络节点和更高的粒度，从而能够以一致且无缝的方式调度作业和对节点进行排序，以实现分布式并行工作负载的最佳性能。

容量预留拓扑 API 已在以下 AWS 区域推出：美国东部 (弗吉尼亚北部)、美国东部 (俄亥俄)、美国西部 (北加州)、美国西部 (俄勒冈)、非洲 (开普敦)、亚太地区 (雅加达)、亚太地区 (香港)、亚太地区 (海得拉巴)、亚太地区 (墨尔本)、亚太地区 (孟买)、亚太地区 (大阪)、亚太地区 (首尔)、亚太地区 (新加坡)、亚太地区 (悉尼)、亚太地区 (东京)、加拿大 (中部)、欧洲 (法兰克福)、欧洲 (爱尔兰)、欧洲 (伦敦)、欧洲 (巴黎)、欧洲 (西班牙)、欧洲 (斯德哥尔摩)、欧洲 (苏黎世)、中东 (巴林)、中东 (阿联酋) 和南美洲 (圣保罗)，并且支持所有可通过实例拓扑 API 使用的实例。

要了解更多信息，请访问最新的 [EC2 用户指南](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-topology.html) 。

---

# AWS Cloud Map 现已在 AWS GovCloud (US) 区域支持跨账户工作负载
发布于：2025年10月30日

AWS Cloud Map 现已通过与 AWS Resource Access Manager (AWS RAM) 集成，在 AWS GovCloud (US) 区域 (AWS GovCloud (US) Regions) 支持跨账户服务发现 (cross-account service discovery)。此项增强功能使您能够跨 AWS 账户 (AWS accounts) 无缝管理和发现云资源 (cloud resources)，例如 Amazon ECS 任务、Amazon EC2 实例和 Amazon DynamoDB 表。通过 AWS RAM 共享您的 AWS Cloud Map 命名空间 (namespace)，其他账户中的工作负载 (workloads) 就可以发现并管理在该命名空间中注册的资源。对于采用多账户架构 (multi-account architectures) 的组织而言，此项增强功能简化了资源共享，减少了资源重复，并促进了跨环境的一致性服务发现。

您现在可以使用 AWS RAM 将您的 AWS Cloud Map 命名空间与单个 AWS 账户、特定的组织单元 (Organizational Units, OUs) 或整个 AWS Organization 共享。要开始使用，请在 AWS RAM 中创建一个资源共享 (resource share)，添加您希望共享的命名空间，并指定应有权访问的主体 (principals) (账户、OUs 或整个组织)。这使得平台工程师 (platform engineers) 能够维护一个集中式服务注册表 (centralized service registry) 或一小组注册表，并在多个账户之间共享，从而简化服务发现。应用开发者 (Application developers) 随后可以构建依赖于一致、共享注册表的服务，而无需担心跨账户的可用性或同步问题。AWS Cloud Map 的跨账户服务发现支持通过减少资源重复和简化对命名空间的访问，提高了运营效率 (operational efficiency)，并使您的组织在发展过程中更容易扩展服务发现能力。

此功能现已在 AWS GovCloud (US-East) 和 AWS GovCloud (US-West) 区域推出，您可以通过 AWS 管理控制台 (AWS Management Console)、API、SDK、CLI 和 CloudFormation 使用。要了解更多信息，请参阅 AWS Cloud Map [文档](https://docs.aws.amazon.com/cloud-map/latest/dg/sharing-namespaces.html) 。

---

# SAP on AWS GROW 针对 SAP Cloud ERP 推出新的区域可用性
发布于: 2025 年 10 月 31 日

SAP Cloud ERP on AWS (GROW) 现已在欧洲 (法兰克福) 区域推出。作为一个集解决方案、最佳实践、采用加速服务、社区和学习资源于一体的完整产品，SAP Cloud ERP on AWS (GROW) 帮助任何规模的组织在全球最全面、应用最广泛的云上，以高速度、高可预测性和持续创新的方式采用云企业资源规划 (ERP) (Enterprise Resource Planning)。与传统的本地 ERP 部署相比，SAP Cloud ERP on AWS (GROW) 的实施时间可以从数年缩短至数月。

通过实施 SAP Cloud ERP on AWS (GROW)，您可以简化日常工作、促进业务增长并确保成功。SAP Cloud ERP on AWS (GROW) 的核心是 SAP S/4HANA Cloud, Public edition，这是一个功能齐全的 SaaS ERP 套件，它基于 SAP 50 多年的行业最佳实践经验构建而成。SAP Cloud ERP on AWS (GROW) 允许您的组织通过集成人力资源、采购、销售、财务、供应链和制造等系统，获得端到端的流程可见性和控制力。它还包括由 SAP Business AI 驱动并利用 AWS 的流程，以提供数据驱动的洞察和建议。客户还可以通过 SAP 生成式 AI 中心的 Amazon Bedrock 模型，利用其 SAP 数据进行生成式 AI (Generative AI) 创新。SAP Cloud ERP on AWS (GROW) 利用了 AWS Graviton 处理器，与同等性能的云实例相比，其能耗可降低高达 60%。

要了解有关在 AWS 上部署 SAP Cloud ERP 的更多信息，请浏览 [SAP on AWS 产品页面](https://aws.amazon.com/sap/grow) 。

---

# Amazon Route 53 Resolver 现已支持 AWS PrivateLink
发布于: 2025 年 10 月 31 日

Amazon Route 53 Resolver 现已支持 [AWS PrivateLink](https://aws.amazon.com/privatelink/) 。现在，客户无需通过公共互联网，即可私密地访问和管理 [Route 53 Resolver](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html) 及其所有相关功能 (包括 Resolver 终端节点 (Resolver endpoints)、Route 53 Resolver DNS 防火墙 (Route 53 Resolver DNS Firewall)、Resolver 查询日志记录 (Resolver Query Logging) 以及 Resolver for AWS Outposts)。AWS PrivateLink 通过亚马逊网络，在 VPC、AWS 服务和本地应用程序之间提供安全的私有连接。当通过 AWS PrivateLink 访问 Route 53 Resolver 及其功能时，所有操作 (例如创建、删除、编辑和列出) 都可以通过亚马逊私有网络进行处理。

Amazon Route 53 Resolver 能够以递归方式响应来自 AWS 资源的 DNS 查询，解析公共记录、Amazon VPC 特定的 DNS 名称以及 Amazon Route 53 私有托管区 (private hosted zones)，并且默认在所有 VPC 中可用。Route 53 Resolver 还提供了一些您可以选择启用的功能 (包括 Resolver 终端节点、Route 53 Resolver DNS 防火墙、Resolver 查询日志记录以及 Resolver for AWS Outposts)。您可以在当前所有已支持 Route 53 Resolver 及其相关功能的区域中，将 Resolver 与 AWS PrivateLink 结合使用，这些区域包括 AWS GovCloud (美国) 区域。有关 Resolver 及其功能可用 AWS 区域的更多信息，请参阅[此处](https://docs.aws.amazon.com/general/latest/gr/r53.html) 。

要了解有关 Route 53 Resolver 及其功能的更多信息，请参阅服务[文档](https://docs.aws.amazon.com/Route53/latest/APIReference/API_Operations_Amazon_Route_53_Resolver.html) 。

---

# Amazon Route 53 Resolver 现已支持 AWS PrivateLink
**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2026/10/amazon-route53-resolver-supports-aws-privatelink](https://aws.amazon.com/about-aws/whats-new/2026/10/amazon-route53-resolver-supports-aws-privatelink) 
**发布时间:** 2025-10-31
**厂商:** AWS
**类型:** WHATSNEW
---
# Amazon Route 53 Resolver 现已支持 AWS PrivateLink
发布于: 2025 年 10 月 31 日
Amazon Route 53 Resolver 现已支持 [AWS PrivateLink](https://aws.amazon.com/privatelink/) 。客户现在可以私密地访问和管理 [Route 53 Resolver](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html) 及其所有相关功能 (解析器终端节点 (Resolver endpoints)、Route 53 Resolver DNS Firewall、解析器查询日志 (Resolver Query Logging)、Resolver for AWS Outposts)，而无需通过公共互联网。AWS PrivateLink 通过亚马逊网络，在 VPC、AWS 服务和本地应用程序之间提供安全的私有连接。当通过 AWS PrivateLink 访问 Route 53 Resolver 及其功能时，所有操作 (例如创建、删除、编辑和列出) 都可以通过亚马逊私有网络进行处理。
Amazon Route 53 Resolver 会对来自 AWS 资源的 DNS 查询进行递归响应，这些查询涉及公共记录、Amazon VPC 特定的 DNS 名称以及 Amazon Route 53 私有托管区域 (private hosted zones)，并且默认在所有 VPC 中可用。Route 53 Resolver 还提供了一些您可以选择启用的功能 (解析器终端节点、Route 53 Resolver DNS Firewall、解析器查询日志、Resolver for AWS Outposts)。您可以在 **Route 53 Resolver 及其所有相关功能** 当前可用的区域中使用 Resolver 及其功能与 AWS PrivateLink，包括 AWS GovCloud (US) 区域。有关 Resolver 及其功能可用 AWS 区域的更多信息，请参阅 [此处](https://docs.aws.amazon.com/general/latest/gr/r53.html) 。
要了解有关 Route 53 Resolver 及其功能的更多信息，请参阅服务 [文档](https://docs.aws.amazon.com/Route53/latest/APIReference/API_Operations_Amazon_Route_53_Resolver.html) 。

---

# Amazon VPC IPAM 实现前缀列表的自动化更新

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-vpc-ipam-prefix-list-automation/](https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-vpc-ipam-prefix-list-automation/) 

**发布时间:** 2025-10-31

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon VPC IPAM 实现前缀列表的自动化更新

发布于: 2025 年 10 月 31 日

今天，AWS 宣布 Amazon VPC IP 地址管理器 (IPAM) 现已支持使用前缀列表解析器 (PLR) 自动化更新前缀列表。该功能允许网络管理员根据他们在 IPAM 中定义的业务逻辑自动更新前缀列表，从而改善其运营状况并减少管理开销。

通过使用 IPAM PLR，您可以定义业务规则，将前缀列表与来自 VPC、子网和 IPAM 池等各种资源的 IP 地址范围进行同步。然后，您可以根据连接需求，在整个 AWS 环境中的路由表和安全组等资源中引用这些前缀列表。在此之前，您需要根据 AWS 环境的变化手动更新前缀列表以添加或删除 IP 地址范围，这一过程操作复杂且容易出错。IPAM PLR 实现了前缀列表的自动化更新，无需人工干预，从而改善了您的运营状况。

该功能现已在支持 Amazon VPC IPAM 的所有 [AWS 区域](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 上线，包括 AWS 中国区域和 AWS GovCloud (US) 区域。

要了解有关此功能的更多信息，请查看 [AWS IPAM 文档](https://docs.aws.amazon.com/vpc/latest/ipam/automate-prefix-list-updates.html) 。有关定价的详细信息，请参阅 [Amazon VPC 定价页面](https://aws.amazon.com/vpc/pricing/) 上的 IPAM 标签页。

---

# AWS Cloud WAN 现已在另外三个 AWS 区域可用
发布于：2025 年 11 月 4 日

即日起，[AWS Cloud WAN](https://aws.amazon.com/cloud-wan/) 现已在 AWS 亚太 (泰国)、AWS 亚太 (台北) 和 AWS 亚太 (新西兰) 区域推出。

借助 AWS Cloud WAN，您可以使用中央控制面板和网络策略来创建一个跨越多个地点和网络的全球网络，从而无需再使用不同技术来配置和管理不同的网络。您可以使用网络策略来指定希望通过 AWS Site-to-Site VPN、AWS Direct Connect 或第三方软件定义广域网 (SD-WAN) 产品连接的 Amazon Virtual Private Clouds、AWS Transit Gateways 和本地位置。AWS Cloud WAN 的中央控制面板会生成网络的全面视图，以帮助您监控网络的运行状况、安全性和性能。此外，AWS Cloud WAN 使用边界网关协议 (BGP) 自动创建跨 AWS 区域的全球网络，使您可以轻松地在全球范围内交换路由。

要了解更多信息，请访问 AWS Cloud WAN [产品详情页面](https://aws.amazon.com/cloud-wan/) 。

---

# Amazon Cloudfront 为 Anycast 静态 IP 添加 IPv6 支持

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/cloudfront-anycast-ipv6-support/](https://aws.amazon.com/about-aws/whats-new/2025/11/cloudfront-anycast-ipv6-support/) 

**发布时间:** 2025-11-05

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon Cloudfront 为 Anycast 静态 IP 添加 IPv6 支持

发布于: 2025年11月5日

Amazon CloudFront 现已支持为 Anycast 静态 IP (Anycast Static IP) 配置 IPv4 和 IPv6 地址。此前，该功能仅限于 IPv4 地址。此次更新后，客户在使用 CloudFront Anycast 静态 IP 地址时可以同时拥有 IPv4 和 IPv6 地址。

过去，客户在使用 CloudFront Anycast 静态 IP 地址时只能使用 IPv4 地址。本次发布后，使用 CloudFront Anycast 静态 IP 地址的客户将为其工作负载同时获得 IPv4 和 IPv6 地址。这种双栈 (dual-stack) 支持使客户能够满足 IPv6 合规性要求，为其基础设施提供面向未来的保障，并为纯 IPv6 网络上的最终用户提供服务。

CloudFront 在所有边缘站点 (edge locations) 均支持 Anycast 静态 IP 的 IPv6 功能。此功能不包括由 Sinnet 运营的 Amazon Web Services 中国 (北京) 区域和由 NWCD 运营的 Amazon Web Services 中国 (宁夏) 区域。点击 [此处](https://aws.amazon.com/blogs/networking-and-content-delivery/zero-rating-and-ip-address-management-made-easy-cloudfronts-new-anycast-static-ips-explained/) 了解有关 Anycast 静态 IP 的更多信息，或参阅 [Amazon CloudFront 开发人员指南](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/request-static-ips.html) 。有关定价信息，请访问 [CloudFront 定价](https://aws.amazon.com/cloudfront/pricing/) 页面。

---

# Amazon CloudFront 宣布为 VPC 源提供跨账户支持

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-cloudfront-cross-account-vpc-origins/](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-cloudfront-cross-account-vpc-origins/) 

**发布时间:** 2025-11-06

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon CloudFront 宣布为 VPC 源提供跨账户支持

发布于: 2025 年 11 月 6 日

Amazon CloudFront 宣布为虚拟私有云 (Virtual Private Cloud, VPC) 源提供跨账户支持，允许客户从其 CloudFront 分配访问位于不同 AWS 账户中的 VPC 源。通过 VPC 源，客户可以将其应用程序负载均衡器 (Application Load Balancers, ALB)、网络负载均衡器 (Network Load Balancers, NLB) 和 EC2 实例置于私有子网中，并且这些资源只能通过其 CloudFront 分配进行访问。借助 CloudFront 对跨账户 VPC 源的支持，客户现在可以利用 VPC 源的安全优势，同时保持其现有的多账户架构。

客户通常会设置多个 AWS 账户以实现更好的安全隔离、成本管理和合规性。以前，客户只有在 CloudFront 和源站位于同一 AWS 账户时，才能从 CloudFront 访问私有 VPC 中的源。这意味着，如果客户的源站分布在多个 AWS 账户中，他们必须将这些账户置于公有子网内，才能获得 CloudFront 带来的规模和性能优势。这样一来，客户就不得不在边缘和区域内部署额外的安全控制措施，例如访问控制列表 (access control lists, ACL)，而无法享受 VPC 源固有的安全性。现在，客户可以使用 [AWS Resource Access Manager (RAM)](https://aws.amazon.com/ram/)  允许 CloudFront 访问不同 AWS 账户中私有 VPC 内的源，无论这些账户是否在其 AWS Organizations 或组织单元 (organizational units, OUs) 内外。这简化了安全管理并降低了运营复杂性，使客户可以轻松地将 CloudFront 用作其应用程序的统一入口。

VPC 源功能仅在 AWS 商业区域提供，支持的 AWS 区域完整列表可在此处[查看](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-vpc-origins.html#vpc-origins-supported-regions) 。将 CloudFront 与跨账户 VPC 源结合使用不会产生额外费用。要了解有关实施跨账户 VPC 源和多账户架构最佳实践的更多信息，请访问 [CloudFront VPC 源文档](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-vpc-origins.html) 。

---

# Amazon VPC Lattice 现已支持为资源配置使用自定义域名

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-vpc-lattice-custom-domain-name-resource-configuration](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-vpc-lattice-custom-domain-name-resource-configuration) 

**发布时间:** 2025-11-07

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon VPC Lattice 现已支持为资源配置使用自定义域名

发布于: 2025 年 11 月 7 日

即日起，VPC Lattice 允许您为资源配置 (resource configuration) 指定自定义域名。资源配置支持跨 VPC 和账户对数据库、集群、域名等资源进行第 4 层 (layer-4) 访问。借助此功能，您可以将资源配置用于基于集群和基于 TLS 的资源。

资源所有者可以通过为资源配置指定自定义域名并与消费者共享该资源配置来使用此功能。随后，消费者可以使用该自定义域名访问资源，VPC Lattice 会在消费者的 VPC 中管理一个私有托管区 (private hosted zone)。

此功能还为资源所有者和消费者提供了对其所需使用的域名的控制权和灵活性。资源所有者可以使用自己、AWS 或第三方拥有的自定义域名。消费者可以使用精细化控制来选择希望 VPC Lattice 为哪些域名管理私有托管区。

此功能在所有已支持 VPC Lattice 资源配置的 AWS 区域 (AWS Regions) 免费提供。要了解更多信息，请阅读我们的 [博客](https://aws.amazon.com/blogs/networking-and-content-delivery/custom-domain-names-for-vpc-lattice-resources/) 或访问 [Amazon VPC Lattice 产品详情页面](https://aws.amazon.com/vpc/lattice/) 和 [Amazon VPC Lattice 文档](https://docs.aws.amazon.com/vpc-lattice/latest/ug/resource-configuration.html)。

---

# Amazon S3 Express One Zone 现已支持互联网协议第 6 版 (IPv6)

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-s3-express-one-zone-ipv6](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-s3-express-one-zone-ipv6) 

**发布时间:** 2025-11-10

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon S3 Express One Zone 现已支持互联网协议第 6 版 (IPv6)

发布于: 2025 年 11 月 10 日

Amazon S3 Express One Zone 现已支持通过网关虚拟私有云 (VPC) 终端节点使用互联网协议第 6 版 (IPv6) 地址。S3 Express One Zone 是一种专为延迟敏感型应用设计的高性能存储类 (storage class)。

许多组织正在采用 IPv6 网络，以缓解其私有网络中的 IPv4 地址耗尽问题或满足合规性要求。您现在可以通过 IPv6 或双栈 (DualStack) VPC 终端节点访问 S3 Express One Zone 中的数据。您无需额外的基础设施来处理 IPv6 到 IPv4 的地址转换。

S3 Express One Zone 对 IPv6 的支持已在所有提供 [该存储类](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-express-Endpoints.html) 的 AWS 区域 (AWS Regions) 中提供，无需额外费用。您可以使用 AWS 管理控制台 (AWS Management Console)、AWS CLI、AWS SDK 或 AWS CloudFormation 为新的和现有的 VPC 终端节点设置 IPv6。要开始在 S3 Express One Zone 上使用 IPv6，请访问 [S3 用户指南](https://docs.aws.amazon.com/AmazonS3/latest/userguide/directory-bucket-az-networking.html#s3-express-networking-vpc-gateway) 。

---

# AWS 为 Amazon S3 网关和接口 VPC 终端节点增加 IPv6 支持
**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/ipv6-amazon-s3-gateway-interface-vpc-endpoints/](https://aws.amazon.com/about-aws/whats-new/2025/11/ipv6-amazon-s3-gateway-interface-vpc-endpoints/) 
**发布时间:** 2025-11-10
**厂商:** AWS
**类型:** WHATSNEW
---
# AWS 为 Amazon S3 网关和接口 VPC 终端节点增加 IPv6 支持
发布于: 2025-11-10
Amazon Web Services (AWS) 现已为 Amazon S3 的 AWS PrivateLink 网关和接口虚拟私有云 (VPC) 终端节点提供互联网协议第 6 版 (IPv6) 地址支持。
互联网的持续发展正在耗尽可用的互联网协议第 4 版 (IPv4) 地址。IPv6 将可用地址的数量增加了几个数量级，客户不再需要在其 VPC 中管理重叠的地址空间。要在一个新的或现有的 S3 网关或接口终端节点上开始使用 IPv6 连接，请将该终端节点的 IP 地址类型配置为 IPv6 或双栈 (Dualstack) 。启用后，对于网关终端节点，Amazon S3 会自动使用 IPv6 地址更新路由表；对于接口终端节点，则会设置一个带有 IPv6 地址的 [弹性网络接口](https://aws.amazon.com/blogs/aws/new-elastic-network-interfaces-in-the-virtual-private-cloud/) (Elastic network interface, ENI) 。
Amazon S3 的 VPC 终端节点对 IPv6 的支持现已在所有 AWS 商业区域 (AWS Commercial Regions) 和 AWS GovCloud (US) 区域推出，无需额外费用。您可以通过 AWS 管理控制台 (AWS Management Console) 、AWS CLI、AWS SDK 或 AWS CloudFormation 为新的和现有的 VPC 终端节点设置 IPv6。要了解更多信息，请参阅服务 [文档。](https://docs.aws.amazon.com/AmazonS3/latest/userguide/privatelink-interface-endpoints.html)

---

# Application Load Balancer 支持客户端凭证流的 JWT 验证

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/application-load-balancer-jwt-verification](https://aws.amazon.com/about-aws/whats-new/2025/11/application-load-balancer-jwt-verification) 

**发布时间:** 2025-11-12

**厂商:** AWS

**类型:** WHATSNEW

---
# Application Load Balancer 支持客户端凭证流的 JWT 验证

发布于: 2025-11-12

Amazon Web Services (AWS) 宣布为 Application Load Balancer (ALB) 推出 JWT 验证功能，以实现安全的机器对机器 (M2M) 和服务对服务 (S2S) 通信。该功能允许 ALB 验证请求头中包含的 JSON Web Tokens (JWTs)，对令牌签名、过期时间和声明 (claims) 进行校验，而无需修改应用程序代码。

通过将 OAuth 2.0 令牌验证卸载到 ALB，客户可以显著降低架构复杂性并简化其安全实施。此功能对于微服务 (microservices) 架构、API 安全以及企业服务集成等需要关键服务间安全通信的场景尤为重要。该功能支持通过各种 OAuth 2.0 流程 (包括客户端凭证流 (Client Credentials Flow)) 颁发的令牌，从而以最小的运营开销实现集中式令牌验证。

JWT 验证功能现已在所有支持 Application Load Balancer 的 AWS 区域 (Regions) 上线。

要了解更多信息，请访问 [ALB 文档](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-verify-jwt.html) 。

---

# AWS Site-to-Site VPN 宣布推出 5 Gbps 带宽隧道
**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/aws-site-to-site-vpn-5-gbps-bandwidth-tunnels](https://aws.amazon.com/about-aws/whats-new/2025/11/aws-site-to-site-vpn-5-gbps-bandwidth-tunnels) 
**发布时间:** 2025-11-12
**厂商:** AWS
**类型:** WHATSNEW
---
# AWS Site-to-Site VPN 宣布推出 5 Gbps 带宽隧道
发布于: 2025 年 11 月 12 日

AWS Site-to-Site VPN 现已支持每个隧道高达 5 Gbps 带宽的 VPN 连接，相较于现有的 1.25 Gbps 限制提升了 4 倍。这一带宽提升使那些需要为带宽密集型混合应用、大数据迁移和灾难恢复架构提供高容量连接的客户受益，同时还能在 AWS 和其远程站点之间保持流量加密。客户还可以将 5 Gbps VPN 连接用作其高容量 AWS Direct Connect 连接的备份或覆盖网络。

AWS Site-to-Site VPN 是一项完全托管的服务，允许您使用 IP 安全 (IPSec) 隧道在您的数据中心或分支机构与 AWS 资源之间创建安全连接。在此之前，Site-to-Site VPN 每个隧道最高支持 1.25 Gbps 的带宽，客户必须依赖 ECMP (等价多路径) 来逻辑上绑定多个隧道以实现更高的带宽。随着此次发布，客户现在可以将其隧道带宽配置为 5 Gbps，从而减少了部署 ECMP 等复杂协议的需求，同时确保了一致的带宽性能。

此功能已在所有提供 AWS Site-to-Site VPN 的 AWS 商业区域和 AWS GovCloud (美国) 区域上线，但亚太 (墨尔本)、以色列 (特拉维夫)、欧洲 (苏黎世)、加拿大西部 (卡尔加里) 和中东 (阿联酋) 区域除外。要了解更多信息并开始使用，请访问 AWS Site-to-Site VPN [文档](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPNTunnels.html#large-bandwidth-tunnels) 。

---

# AWS Network Load Balancer 现已在直通模式下支持 QUIC 协议

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/aws-network-load-balancer-quic-passthrough-mode/](https://aws.amazon.com/about-aws/whats-new/2025/11/aws-network-load-balancer-quic-passthrough-mode/) 

**发布时间:** 2025-11-13

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Network Load Balancer 现已在直通模式下支持 QUIC 协议

发布于: 2025 年 11 月 13 日

AWS 网络负载均衡器 (Network Load Balancer, NLB) 现已在直通模式 (passthrough mode) 下支持 QUIC 协议，可实现 QUIC 流量的低延迟转发，同时通过 QUIC 连接 ID (Connection ID) 保持会话保持 (session stickiness)。此项增强功能可帮助客户在移动应用程序中维持稳定的连接，即使在网络漫游 (network roaming) 期间客户端 IP 地址发生变化也能不受影响。

通过支持 QUIC，客户可以减少数据包往返 (packet round trips) 次数，从而将应用程序延迟降低高达 30%，并确保在不同网络条件下提供无缝的用户体验。这对于需要用户在蜂窝基站之间移动或从 WiFi 切换到蜂窝网络的移动应用尤其有用，可以避免连接状态丢失。您可以通过 AWS 管理控制台、CLI 或 API 在现有或新的网络负载均衡器上启用 QUIC 支持。启用后，即使客户端发生漫游，NLB 也会使用 QUIC 连接 ID 将 QUIC 流量转发到目标，以维持会话保持。

QUIC 支持已在所有 AWS 商业区域和 AWS GovCloud (US) 区域提供，无需额外付费。QUIC 流量的计量包含在现有的 UDP 负载均衡器容量单位 (Load Balancer Capacity Unit, LCU) 配额内。

要了解更多信息，请访问 [AWS 博客](https://aws.amazon.com/blogs/networking-and-content-delivery/introducing-quic-protocol-support-for-network-load-balancer-accelerating-mobile-first-applications/) 和 [NLB 用户指南](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/create-listener.html#add-listener)。

---

# Amazon Route 53 Profiles 现已支持解析程序查询日志记录配置

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-route-53-profiles-resolver-query-logging-configurations](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-route-53-profiles-resolver-query-logging-configurations) 

**发布时间:** 2025-11-17

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon Route 53 Profiles 现已支持解析程序查询日志记录配置

发布于: 2025年11月17日

今日，AWS 宣布 Amazon Route 53 Profiles 已支持解析程序查询日志记录 (Resolver query logging) 配置，允许您管理解析程序查询日志记录配置，并将其应用于您组织内的多个 VPC 和 AWS 账户。通过此项增强功能，Amazon Route 53 Profiles 简化了解析程序查询日志记录的管理，它优化了将日志记录配置与 VPC 关联的过程，无需您为每个 VPC 手动进行关联。

Route 53 Profiles 允许您创建 Route 53 配置 (私有托管区 (private hosted zones)、DNS 防火墙规则组 (DNS Firewall rule groups)、解析程序规则 (Resolver rules)) 并在多个 VPC 和 AWS 账户之间共享。此前，解析程序查询日志记录需要您在每个 AWS 账户中为每个 VPC 手动进行设置。现在，借助 Route 53 Profiles，您可以使用单个 Profile 配置来管理 VPC 和 AWS 账户的解析程序查询日志记录配置。Profiles 对解析程序查询日志记录配置的支持，通过在所有账户和 VPC 中提供一致的 DNS 查询日志，降低了网络安全团队的管理开销，并简化了合规性审计。

Route 53 Profiles 对解析程序查询日志记录的支持现已在[此处](https://docs.aws.amazon.com/general/latest/gr/r53.html) 提及的 AWS 区域 (AWS Regions) 中提供。要了解有关此功能的更多信息及其为您组织带来的益处，请访问 Amazon Route 53 [文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/profiles.html) 。您可以通过 AWS 管理控制台 (AWS Management Console) 中的 Amazon Route 53 控制台或通过 AWS CLI 开始使用。要了解有关 Route 53 Profiles 定价的更多信息，请参阅[此处](https://aws.amazon.com/route53/pricing/) 。

---

# Amazon Route 53 DNS Firewall 新增针对基于字典的 DGA 攻击的防护功能

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-route-53-dns-firewall-protection-dictionary-dga-attacks](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-route-53-dns-firewall-protection-dictionary-dga-attacks) 

**发布时间:** 2025-11-17

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon Route 53 DNS Firewall 新增针对基于字典的 DGA 攻击的防护功能

发布于: 2025 年 11 月 17 日

从今天开始，您可以启用 Route 53 Resolver DNS Firewall Advanced 来监控和阻止与基于字典的域名生成算法 (Dictionary-based Domain Generation Algorithm, DGA) 攻击相关的查询。这类攻击通过伪随机地拼接预定义字典中的单词来生成域名，从而创建人类可读的字符串以逃避检测。

Route 53 DNS Firewall Advanced 是 Route 53 DNS Firewall 提供的一项功能，它使您能够根据从 VPC 中查询的域名中识别出的异常，实时监控和阻止 DNS 流量，从而实施保护。这些保护措施包括针对 DNS 隧道 (DNS tunneling) 和 DGA 攻击的防护。在此次发布后，您还可以针对基于字典的 DGA 攻击实施保护。这是 DGA 攻击的一种变体，其生成的域名会模仿并混入合法域名中，以抵抗检测。要开始使用，您可以配置一个或多个 DNS Firewall Advanced 规则，并将“基于字典的 DGA”指定为要检查的威胁类型。您可以将这些规则添加到一个 DNS Firewall 规则组中，并通过将该规则组直接关联到每个所需的 VPC，或使用 AWS Firewall Manager、AWS Resource Access Manager (RAM)、AWS CloudFormation 或 Route 53 Profiles，在您的 VPC 上强制执行这些规则。

Route 53 Resolver DNS Firewall Advanced 对基于字典的 DGA 的支持已在所有 AWS 区域 (AWS Regions) 推出，包括 AWS GovCloud (US) 区域。要了解有关新功能和定价的更多信息，请访问 Route 53 Resolver DNS Firewall [网页](https://aws.amazon.com/route53/resolver-dns-firewall/) 和 [Route 53 定价页面](https://aws.amazon.com/route53/pricing/) 。要开始使用，请访问 Route 53 [文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/firewall-advanced.html) 。

---

# Amazon VPC IPAM 实现从 Infoblox IPAM 自动分配 IP

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-vpc-ipam-automates-ip-from-infoblox/](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-vpc-ipam-automates-ip-from-infoblox/) 

**发布时间:** 2025-11-17

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon VPC IPAM 实现从 Infoblox IPAM 自动分配 IP

发布于: 2025 年 11 月 17 日

今日，AWS 宣布 Amazon VPC IP 地址管理器 (IPAM) 现已支持从 Infoblox Universal IPAM 自动获取无重叠的 IP 地址分配。该功能最大限度地减少了云和本地管理员之间的手动流程，缩短了周转时间。

通过此功能，您可以从本地 Infoblox Universal IPAM 自动获取无重叠的 IP 地址到您的顶级 AWS IPAM 池中，并根据业务需求将其组织到区域池中。获取无重叠的 IP 可以降低服务中断的风险，因为您的 IP 不会与本地 IP 地址冲突。此前，在混合云环境中，管理员必须通过工单或电子邮件等线下方式来请求和分配 IP 地址，这通常耗时且容易出错。此次集成将手动流程自动化，从而提高了运营效率。

该功能在所有支持 Amazon VPC IPAM 的 [AWS 区域](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 提供，但不包括 AWS 中国区域和 AWS GovCloud (US) 区域。

要了解有关 IPAM 的更多信息，请查看 [IPAM 文档](https://docs.aws.amazon.com/vpc/latest/ipam/integrate-infoblox-ipam.html) 。有关定价详情，请参阅 [Amazon VPC 定价页面](https://aws.amazon.com/vpc/pricing/) 上的 IPAM 标签页。

---

# AWS 宣布为网站交付与安全推出统一费率定价计划

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/aws-flat-rate-pricing-plans](https://aws.amazon.com/about-aws/whats-new/2025/11/aws-flat-rate-pricing-plans) 
**发布时间:** 2025-11-18
**厂商:** AWS
**类型:** WHATSNEW
---
# AWS 宣布为网站交付与安全推出统一费率定价计划

发布于: 2025-11-18

Amazon Web Services (AWS) 正在为网站交付与安全推出无超额费用的统一费率定价计划。这些统一费率计划可通过 Amazon CloudFront 使用，将全球内容分发与 AWS WAF、DDoS 防护 (DDoS protection)、Amazon Route 53 DNS、Amazon CloudWatch 日志摄取 (Logs ingestion) 以及无服务器边缘计算 (serverless edge compute) 整合为一个**简单的月度价格**，**且无超额费用**。每个计划还包含每月的 Amazon S3 存储抵扣额度，以帮助您抵消存储成本。

CloudFront 统一费率计划让您能够交付网站和应用程序，而无需跨多个 AWS 服务计算成本。即使您的网站或应用程序爆火或遭遇 DDoS 攻击，您也不会面临超额费用的风险。WAF 和 DDoS 防护等安全功能默认启用，并且额外的配置设置简单。当您通过 CloudFront 而非直接通过互联网为您的 AWS 应用程序提供服务时，您的统一费率计划将涵盖应用程序与查看者之间的数据传输成本，以一个简单的月度价格提供服务，无需担心超额费用。这种简化的定价模型与每个 CloudFront 分发 (distribution) 的按需付费 (pay-as-you-go) 定价并行提供，让您可以灵活地为每个应用程序选择合适的定价模型和功能集。

这些计划适用于新的和现有的 CloudFront 分发，分为免费 (每月 0 美元)、专业版 (每月 15 美元)、商业版 (每月 200 美元) 和高级版 (每月 1000 美元) 等套餐等级。您可以选择功能和使用限额 (usage allowances) 与您应用程序需求相匹配的套餐等级。要了解更多信息，请参阅[发布博客](https://aws.amazon.com/blogs/networking-and-content-delivery/introducing-flat-rate-pricing-plans-with-no-overages/) 、[套餐与定价](https://aws.amazon.com/cloudfront/pricing/) 或[CloudFront 开发人员指南](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/flat-rate-pricing-plan.html) 。要开始使用，请访问 [CloudFront 控制台](https://us-east-1.console.aws.amazon.com/cloudfront/v4/home?region=us-east-1#/distributions) 。

---

# AWS Network Firewall 现已默认启用主动威胁防御

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/active-threat-defense-default-network-firewall/](https://aws.amazon.com/about-aws/whats-new/2025/11/active-threat-defense-default-network-firewall/) 

**发布时间:** 2025-11-18

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Network Firewall 现已默认启用主动威胁防御

发布于: 2025 年 11 月 18 日

从即日起，当您在 AWS 管理控制台 (AWS Management Console) 中创建新的防火墙策略时，AWS Network Firewall 将默认在警报模式 (alert mode) 下启用主动威胁防御 (active threat defense)。主动威胁防御功能基于情报驱动，可自动防御在 AWS 基础设施中观察到的动态、持续的威胁活动。

通过此默认设置，您可以深入了解受保护的威胁活动、指标组、类型和威胁名称。您可以切换到拦截模式 (block mode) 以自动阻止可疑流量，例如命令与控制 (C2) 通信、嵌入式 URL 和恶意域名，也可以完全禁用此功能。AWS 会对威胁指标进行验证，以确保高准确性并最大限度地减少误报 (false positives)。

主动威胁防御已在所有提供 AWS Network Firewall 的区域上线，包括 AWS GovCloud (US) 和中国区域 (China Regions)。要了解有关主动威胁防御和定价的更多信息，请参阅 AWS Network Firewall [产品页面](https://aws.amazon.com/network-firewall/) 和 [文档](https://docs.aws.amazon.com/network-firewall/latest/developerguide/aws-managed-rule-groups-atd.html)。

---

# Amazon API Gateway 新增开发者门户功能

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/api-gateway-developer-portal-capabilities/](https://aws.amazon.com/about-aws/whats-new/2025/11/api-gateway-developer-portal-capabilities/) 

**发布时间:** 2025-11-19

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon API Gateway 新增开发者门户功能

发布于: 2025年11月19日

Amazon API Gateway 推出了门户 (Portals) 功能，使企业能够创建完全托管的 AWS 原生开发者门户。这些门户可作为 AWS 资产 (例如 REST API) 的中心枢纽，用于在其整个 AWS 基础设施中进行发现、文档化和治理。门户 (Portals) 通过自动发现跨账户的现有 API、生成文档并支持自定义文档，解决了 API 碎片化的挑战。团队可以将 API 组织成面向不同受众的逻辑产品，通过附加公司徽标来自定义品牌，配置访问控制，确保 API 符合组织标准，并利用分析功能了解用户参与度。用户可以从发现功能和“试用” (Try It) 按钮中受益，轻松进行 API 探索。

门户 (Portals) 提供了三大优势，解决了当今 API 管理中紧迫的挑战。它们将所有 API 配置保留在 AWS 边界内，同时为内部和外部受众提供访问控制，从而消除了第三方解决方案的安全风险。门户还通过自动化门户生成以及随 API 演进自动更新的文档，将开发者的入门时间从数周缩短至几分钟。这不仅免去了数周的基础设施设置工作，还促进了跨开发团队的复用。此外，门户通过 CloudWatch RUM (真实用户监控) 提供了对开发者门户使用情况和分析的可见性，使理解用户参与度变得更加容易。

要了解此功能的定价，请参阅 [Amazon API Gateway 定价页面](https://aws.amazon.com/api-gateway/pricing/) 。Amazon API Gateway 门户 (Portals) 已在所有 AWS 区域 (Region) 提供，不包括 AWS GovCloud (美国) 和中国区域。要开始使用，请访问 Amazon [API Gateway 文档](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-portals.html) 和 [AWS 博客文章](https://aws.amazon.com/blogs/compute/improve-api-discoverability-with-the-new-amazon-api-gateway-portal/) 。

---

# Amazon VPC IPAM 现已支持策略以强制执行 IP 分配策略

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-vpc-ipam-policies-ip-allocation-strategy/](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-vpc-ipam-policies-ip-allocation-strategy/) 

**发布时间:** 2025-11-19

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon VPC IPAM 现已支持策略以强制执行 IP 分配策略

发布于: 2025 年 11 月 19 日

Amazon Virtual Private Cloud (VPC) IP 地址管理器 (IPAM) 支持策略，可用于集中配置和强制执行您期望的 IP 分配策略。这可以确保资源使用来自特定 IPAM 池的公有 IPv4 地址启动，从而改善运维态势，并简化网络和安全管理。

通过使用 IPAM 策略，IP 管理员可以为 AWS 资源 (例如在区域可用性模式下使用的网络地址转换 (NAT) 网关和弹性 IP 地址) 集中定义公有 IP 分配规则。集中配置的 IP 分配策略不能被单个应用团队覆盖，从而确保始终保持合规性。在此功能推出之前，IP 管理员必须对整个组织内的应用所有者进行培训，并依赖他们始终遵守 IP 分配最佳实践。IPAM 策略可以大幅改善您的运营模式。现在，您可以放心地在访问控制列表、路由表、安全组和防火墙等网络和安全组件中添加基于 IP 的筛选器，因为分配给 AWS 资源的公有 IPv4 地址始终来自特定的 IPAM 池。

该功能已在所有 AWS 商业区域和 AWS GovCloud (美国) 区域的 VPC IPAM 免费套餐和高级套餐中提供。当与 VPC IPAM 的高级套餐结合使用时，客户可以跨 AWS 账户和 AWS 区域设置策略。要开始使用，请参阅 [IPAM 策略文档页面](https://docs.aws.amazon.com/vpc/latest/ipam/define-public-ipv4-allocation-strategy-with-ipam-policies.html) 。

要了解有关 IPAM 的更多信息，请查看 [IPAM 文档](https://docs.aws.amazon.com/vpc/latest/ipam/what-it-is-ipam.html) 。有关定价详情，请参阅 [Amazon VPC 定价页面](https://www.amazonaws.cn/en/vpc/pricing/) 上的 IPAM 选项卡。

---

# AWS PrivateLink 现已支持 AWS 服务的跨区域连接
**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/aws-privatelink-cross-region-connectivity-aws-services](https://aws.amazon.com/about-aws/whats-new/2025/11/aws-privatelink-cross-region-connectivity-aws-services)
**发布时间:** 2025-11-19
**厂商:** AWS
**类型:** WHATSNEW
---
# AWS PrivateLink 现已支持 AWS 服务的跨区域连接
发布于：2025 年 11 月 19 日

AWS PrivateLink 现已支持与 AWS 服务的原生跨区域连接。在此之前，接口 VPC 终端节点 (Interface VPC endpoints) 仅支持连接到同一区域 (Region) 内的 AWS 服务。此次发布使客户能够通过接口终端节点连接到同一 AWS [分区 (partition)](https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/partitions.html#:~:text=AWS%20groups%20Regions%20into%20partitions,resources%20in%20a%20different%20partition.) 内其他区域中托管的特定 AWS 服务。

作为服务使用者，您可以私密地访问 Amazon S3、Route53、Elastic Container Registry (ECR) 及其他服务，无需设置跨区域对等连接 (cross-region peering) 或将数据暴露在公共互联网上。这些服务可以通过您 VPC 中的私有 IP 地址，经由接口终端节点进行访问，从而实现更简单、更安全的区域间连接。此功能可帮助您构建符合数据驻留 (data residency) 要求的全球分布式私有网络，同时通过 PrivateLink 访问受支持的 AWS 服务。

要了解此功能的定价信息，请参阅 [AWS PrivateLink 定价页面](https://aws.amazon.com/privatelink/pricing/) 。有关受支持的 AWS 服务和区域的完整列表，请参阅我们的[文档](https://docs.aws.amazon.com/vpc/latest/privatelink/aws-services-cross-region-privatelink-support.html) 和[发布博客](https://aws.amazon.com/blogs/networking-and-content-delivery/aws-privatelink-extends-cross-region-connectivity-to-aws-services/) 。要了解更多信息，请访问 Amazon VPC 开发人员指南中的 [*AWS PrivateLink*](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html) 。

---

# Amazon API Gateway 现已为 REST API 提供额外的 TLS 安全策略支持

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-api-gateway-tls-security-rest-apis/](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-api-gateway-tls-security-rest-apis/) 

**发布时间:** 2025-11-19

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon API Gateway 现已为 REST API 提供额外的 TLS 安全策略支持

发布于: 2025 年 11 月 19 日

Amazon API Gateway 现已在 API 端点和自定义域名上支持增强的 TLS 安全策略，让您能够更好地控制 API 的安全状况。这些新策略可帮助您满足不断变化的安全要求，遵守更严格的法规，并增强 API 连接的加密。

在配置 REST API 和自定义域名时，您现在可以从一个扩展的安全策略列表中进行选择，包括仅要求 TLS 1.3、实现完全正向保密 (Perfect Forward Secrecy)、符合联邦信息处理标准 (Federal Information Processing Standard, FIPS) 或利用后量子密码学 (Post Quantum Cryptography) 的选项。这些策略有助于满足不断变化的安全要求和更严格的法规，同时简化 API 安全管理。增强的策略还支持端点访问控制，以实现额外的治理。

API Gateway 增强的 TLS 安全策略已在以下 AWS 商业区域推出：美国东部 (弗吉尼亚北部)、美国东部 (俄亥俄)、美国西部 (北加利福尼亚)、美国西部 (俄勒冈)、非洲 (开普敦)、亚太地区 (香港)、亚太地区 (海得拉巴)、亚太地区 (雅加达)、亚太地区 (马来西亚)、亚太地区 (墨尔本)、亚太地区 (孟买)、亚太地区 (大阪)、亚太地区 (首尔)、亚太地区 (新加坡)、亚太地区 (悉尼)、亚太地区 (东京)、加拿大 (中部)、加拿大西部 (卡尔加里)、欧洲 (法兰克福)、欧洲 (爱尔兰)、欧洲 (伦敦)、欧洲 (米兰)、欧洲 (巴黎)、欧洲 (西班牙)、欧洲 (斯德哥尔摩)、欧洲 (苏黎世)、以色列 (特拉维夫)、中东 (阿联酋)、南美洲 (圣保罗)。

要了解更多信息，请访问 [Amazon API Gateway 文档](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-security-policies.html) 。

---

# Amazon Route 53 DNS 服务现已支持 AWS PrivateLink
**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-route-53-dns-service-aws-privatelink/](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-route-53-dns-service-aws-privatelink/) 
**发布时间:** 2025-11-19
**厂商:** AWS
**类型:** WHATSNEW
---
# Amazon Route 53 DNS 服务现已支持 AWS PrivateLink
发布于: 2025年11月19日

Amazon Route 53 现已支持通过 [AWS PrivateLink](https://aws.amazon.com/privatelink/)  向 `route53.amazonaws.com` 服务终端节点发送 API 请求，这使得您的 AWS 工作负载无需使用公有互联网即可更改关键的 DNS 基础设施，包括托管区域 (hosted zones)、记录 (records) 和运行状况检查 (health checks)。通过此次发布，您可以在任何 AWS 区域，通过 AWS 骨干网在您的虚拟私有云 (VPCs) 和 Route 53 API 之间建立私有连接。

客户使用 Route 53 API 进行域名系统 (DNS) 操作，这些操作是其云基础设施自动化、面向用户的应用程序和内部服务的基础层。此集成简化了云架构，客户不再需要设置和管理复杂的网络服务来将其虚拟私有云 (VPCs) 中的资源私密地连接到 Route 53 API。现在，客户可以在其 VPC 内部使用 VPC 终端节点 (VPC endpoint) 来建立与 Route 53 API 的连接。位于 `us-east-1` 区域之外的客户可以使用跨区域接口 VPC 终端节点 (cross-region Interface VPC endpoints)  从其他区域本地连接到 Route 53，无需通过公有互联网发送流量，也无需设置 VPC 对等连接 (VPC peering) 等区域间连接。

Route 53 对 PrivateLink 的支持已在全球范围内提供，但不包括 AWS GovCloud 和中国区的 Amazon Web Services。要了解有关此功能的更多信息或开始使用，请访问 [AWS PrivateLink 文档](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html) 。要了解定价信息，请访问 [PrivateLink 定价页面](https://aws.amazon.com/privatelink/pricing/) 。

---

# Amazon API Gateway 现已支持 REST API 的响应流式传输

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/api-gateway-response-streaming-rest-apis/](https://aws.amazon.com/about-aws/whats-new/2025/11/api-gateway-response-streaming-rest-apis/) 

**发布时间:** 2025-11-19

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon API Gateway 现已支持 REST API 的响应流式传输

发布于: 2025 年 11 月 19 日

Amazon API Gateway 现已支持在响应负载 (response payloads) 可用时，以流式方式逐步将其传输给客户端。这无需在传输前缓冲完整的响应，从而提高了 REST API 的响应能力。这项新功能适用于支持流式传输的后端，包括 Lambda 函数、HTTP 代理集成和私有集成。

响应流式传输 (Response streaming) 带来三大核心优势：提升首字节时间 (time-to-first-byte, TTFB) 性能、将集成超时时间延长至 15 分钟，以及支持超过 10 MB 的负载。生成式 AI (Generative AI) 应用尤其能从 TTFB 的提升中获益，因为用户可以实时地看到响应内容逐步呈现；而那些需要更长处理时间的复杂推理模型，现在也可以在延长的超时时间内运行。此外，对大负载的支持使得可以直接流式传输媒体文件和大型数据集，无需再使用预签名 Amazon S3 URL (pre-signed Amazon S3 URLs) 等变通方案。

要了解该功能的定价信息，请参阅 Amazon API Gateway 定价页面。Amazon API Gateway 的响应流式传输功能已在所有 AWS 区域 (AWS Regions) 提供，包括 AWS GovCloud (US) 区域，并支持区域、私有和边缘优化终端节点。要开始使用，请访问 [Amazon API Gateway 文档](https://docs.aws.amazon.com/apigateway/latest/developerguide/response-transfer-mode.html) 、[AWS 博客](https://aws.amazon.com/blogs/compute/building-responsive-apis-with-amazon-api-gateway-response-streaming/) 和 [客户成功案例博客](https://aws.amazon.com/blogs/architecture/building-an-ai-gateway-to-amazon-bedrock-with-amazon-api-gateway/) 。

---

# AWS Network Load Balancer 支持加权目标组，简化部署流程
发布于: 2025年11月19日
Network Load Balancer 现已支持加权目标组 (weighted target groups)，允许您通过可配置的权重将流量分配到多个目标组，以实现高级部署策略。
加权目标组支持蓝绿部署 (Blue-Green Deployments)、金丝雀部署 (Canary Deployments)、应用迁移 (Application Migration) 和 A/B 测试 (A/B Testing) 等关键用例。您可以通过注册多个目标组，并为其配置 0 到 999 范围内的权重，从而精确控制流量分发。蓝绿部署和金丝雀部署允许您在不同应用版本之间逐步切换流量，从而在升级和打补丁时最大限度地减少停机时间；应用迁移能够在不中断生产流量的情况下，实现从旧有技术栈到新栈的无缝过渡；而 A/B 测试则有助于将传入流量分配到不同的实验环境中。所有目标组类型均受支持，包括实例、IP 地址和 Application Load Balancer (ALB) 目标。
加权目标组路由功能已在所有 AWS 商业区域和 AWS GovCloud (US) 区域推出，适用于所有现有和新建的 Network Load Balancer，无需额外费用。该功能将按标准的负载均衡器容量单位 (Load Balancer Capacity Unit, LCU) 价格计费。
要了解更多信息，请参阅 [这篇 AWS 博客文章](https://aws.amazon.com/blogs/networking-and-content-delivery/network-load-balancers-now-support-weighted-target-groups/) 和 [NLB 用户指南](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/listener-update-rules.html)。

---

# AWS Site-to-Site VPN 推出 VPN 集中器

发布于: 2025-11-19

AWS Site-to-Site VPN 推出 VPN 集中器 (VPN Concentrator)，这是一项为分布式企业简化多站点连接的新功能。VPN 集中器适用于需要将 25 个以上远程站点连接到 AWS 的客户，且每个站点的带宽需求较低 (低于 100 Mbps)。

在此之前，需要将大量低带宽远程站点连接到 AWS 的客户依赖于一些使用复杂的解决方案。这些解决方案会产生额外的运维开销，因为客户需要在 AWS 中部署和管理多个虚拟设备。例如，客户需要负责在多个可用区 (availability zones) 中部署设备并进行网络配置，以确保高可用性。AWS Site-to-Site VPN 是一项完全托管的服务，允许您使用 IP 安全 (IPSec) 隧道在数据中心或分支机构与您的 AWS 资源之间建立安全连接。此次发布后，客户现在可以使用单个 VPN 集中器连接多达 100 个低带宽站点，以访问其在 AWS 中的工作负载。VPN 集中器通过允许多个远程站点通过单个到 AWS Transit Gateway 的附件进行连接，从而简化了多站点连接。使用 VPN 集中器聚合大量低带宽站点还能实现高效的带宽利用，进而降低每个站点的 VPN 成本。

该功能已在所有提供 AWS Site-to-Site VPN 的 AWS 商业区域和 AWS GovCloud (美国) 区域上线。要了解更多信息并开始使用，请访问 AWS Site-to-Site VPN [文档](https://docs.aws.amazon.com/vpn/latest/s2svpn/vpn-concentrator.html) 。

---

# AWS NAT 网关现已支持区域可用性

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/aws-nat-gateway-regional-availability](https://aws.amazon.com/about-aws/whats-new/2025/11/aws-nat-gateway-regional-availability)

**发布时间:** 2025-11-19

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS NAT 网关现已支持区域可用性

发布于: 2025年11月19日

Amazon Web Services (AWS) 宣布为 NAT 网关 (NAT Gateway) 推出区域可用性模式。通过此次发布，您可以创建一个单一的 NAT 网关，它会根据您的工作负载 (workload) 分布，在您的 Virtual Private Cloud (VPC) 中的多个可用区 (AZ) 之间自动扩展和收缩，从而在简化设置和管理的同时保持高可用性 (high availability)。

NAT 网关使私有子网 (private subnet) 中的实例能够使用 NAT 网关的 IP 地址连接到 VPC 外部的服务。在此次发布后，您可以创建一个 NAT 网关并将其可用性设置为区域性。您不再需要公共子网 (public subnet) 来托管区域性 NAT 网关。当您的工作负载扩展到新的可用区时，您也无需再创建和删除 NAT 网关，或编辑您的路由表 (route table)。您只需创建一个区域模式的 NAT 网关，选择您的 VPC，它就会根据您工作负载的分布在所有可用区中自动扩展和收缩，从而保持高可用性。您可以使用 Amazon 提供的 IP 地址或自带 IP 地址来使用此功能。

该功能已在所有商业 AWS 区域 (Region) 上线，但 AWS GovCloud (US) 区域和中国区域除外，**可通过 CLI 和 SDK 使用**。要了解有关 VPC NAT 网关和此功能的更多信息，请访问我们的 [文档](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html) 。

---

# Amazon EKS 推出增强型容器网络可观测性

发布于: 2025年11月19日

今天，我们宣布在 [Amazon Elastic Kubernetes Service (EKS)](https://aws.amazon.com/eks/) 中推出新的网络可观测性 (network observability) 功能，为您的容器网络环境提供更深入的洞察。这些新功能可帮助您更好地理解、监控和排查在 AWS 上的 Kubernetes 网络环境。

客户越来越多地通过部署微服务 (microservices) 来在 AWS 云上扩展软件并进行增量创新，同时使用 Amazon EKS 作为运行其应用程序的底层平台。借助增强型容器网络可观测性，客户可以利用细粒度的网络相关指标，更好地对集群流量、跨可用区 (AZ) 流量和 AWS 服务进行主动异常检测。通过这些指标，客户可以更好地衡量系统性能，并使用其偏好的可观测性技术栈将底层指标可视化。

此外，EKS 现在在 AWS 控制台中提供了网络监控可视化功能，可加速并增强精准的故障排查，从而实现更快的根因分析。客户还可以利用这些可视化功能，精确定位导致重传和重传超时的 top-talkers (流量大户) 和网络流，从而消除事件期间的监控盲点。EKS 中的这些网络监控功能由 [Amazon CloudWatch Network Flow Monitor](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-NetworkFlowMonitor.html) 提供支持。

EKS 的增强型容器网络可观测性已在所有支持 CloudWatch Network Flow Monitor 的商业 AWS [区域](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-NetworkFlowMonitor-Regions.html) 上线。要了解更多信息，请访问 [Amazon EKS 文档](https://docs.aws.amazon.com/eks/latest/userguide/network-observability.html) 和 [AWS 新闻发布博客](https://aws.amazon.com/blogs/aws/monitor-network-performance-and-traffic-across-your-eks-clusters-with-container-network-observability/)。

---

# AWS Application Load Balancer 推出 Target Optimizer

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/aws-application-load-balancer-target-optimizer](https://aws.amazon.com/about-aws/whats-new/2025/11/aws-application-load-balancer-target-optimizer)

**发布时间:** 2025-11-20

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Application Load Balancer 推出 Target Optimizer

发布于: 2025 年 11 月 20 日

Application Load Balancer (ALB) 现已推出 Target Optimizer，这是一项新功能，可让您对目标 (target) 强制执行最大并发请求 (concurrent requests) 数量。

通过 Target Optimizer，您可以微调您的应用程序堆栈 (application stack)，使目标仅接收其能够处理的请求数量，从而实现更高的请求成功率、更高的目标利用率 (target utilization) 和更低的延迟 (latency)。这对于计算密集型工作负载 (compute-intensive workloads) 尤其有用。例如，如果您的应用程序执行复杂的数据处理或推理 (inference)，您可以将每个目标配置为一次只接收一个请求，以确保并发请求数量与目标处理能力相匹配。

您可以通过创建一个带有目标控制端口 (target control port) 的新目标组 (target group) 来启用此功能。启用后，该功能需要借助一个由 AWS 提供的代理 (agent) 来工作，您需要在目标上运行该代理来跟踪请求并发度。对于每个 ALB 包含多个目标组的部署，您可以灵活地为每个目标组单独配置此功能。

您可以通过 AWS Management Console、AWS CLI、AWS SDK 和 AWS API 启用 Target Optimizer。ALB Target Optimizer 已在所有 AWS 商业区域 (AWS Commercial Regions)、AWS GovCloud (US) 区域和 AWS 中国区域上线。与常规目标组相比，启用了 Target Optimizer 的目标组流量会产生更多的 LCU 用量。有关更多信息，请参阅 [定价页面](https://aws.amazon.com/elasticloadbalancing/pricing/?nc=sn&loc=3) 、[发布博客](https://aws.amazon.com/blogs/networking-and-content-delivery/drive-application-performance-with-application-load-balancer-target-optimizer/) 和 ALB [用户指南](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-register-targets.html#register-targets-target-optimizer) 。

---

# Amazon CloudFront 宣布推出 3 项 CloudFront Functions 新功能

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-cloudfront-3-functions-capabilities](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-cloudfront-3-functions-capabilities) 

**发布时间:** 2025-11-20

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon CloudFront 宣布推出 3 项 CloudFront Functions 新功能

发布于：2025 年 11 月 20 日

Amazon CloudFront 现已为 CloudFront Functions 推出三项新功能：边缘站点 (Edge Location) 和区域性边缘缓存 (Regional Edge Cache) 元数据、原始查询字符串检索以及高级源站覆盖。开发者现在可以构建更复杂的边缘计算 (Edge Computing) 逻辑，从而更清晰地洞察 CloudFront 的基础设施，并对源站连接进行精确、细粒度的控制。CloudFront Functions 允许您在 CloudFront 边缘站点运行轻量级 JavaScript 代码，以亚毫秒级的执行时间自定义内容分发并实施安全策略。

边缘站点元数据包含提供服务的边缘站点的三字母机场代码以及预期的区域性边缘缓存信息。这使得实现地理位置特定的内容路由或满足合规性要求成为可能，例如根据客户端位置将欧洲用户定向到符合 GDPR 规范的源站。原始查询字符串功能允许访问从查看器接收到的完整、未经处理的查询字符串，从而保留在标准解析过程中可能被更改的特殊字符和编码。高级源站覆盖功能允许您自定义 SSL/TLS 握手参数，包括服务器名称指示 (Server Name Indication)，从而解决了复杂应用基础设施中的关键挑战。例如，在多租户 (Multi-tenant) 场景中，当 CloudFront 通过解析到不同证书域名的服务器的 CNAME 链进行连接时，可以覆盖 SNI。

这些 CloudFront Functions 新功能已在所有 CloudFront 边缘站点提供，无需额外费用。要了解有关 CloudFront Functions 的更多信息，请参阅 [Amazon CloudFront 开发人员指南](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-functions.html) 。

---

# Amazon CloudFront 现已支持 CBOR Web 令牌和通用访问令牌

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-cloudfront-cbor-tokens](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-cloudfront-cbor-tokens) 

**发布时间:** 2025-11-20

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon CloudFront 现已支持 CBOR Web 令牌和通用访问令牌

发布于: 2025 年 11 月 20 日

Amazon CloudFront 现已支持 [CBOR Web 令牌 (CWT)](https://datatracker.ietf.org/doc/html/rfc8392) 和通用访问令牌 (Common Access Tokens, CAT)，允许用户通过 CloudFront Functions 在 CloudFront 边缘站点实现安全的、基于令牌的身份验证和授权。CWT 采用 [简明二进制对象表示法 (Concise Binary Object Representation, CBOR)](https://datatracker.ietf.org/doc/html/rfc8949) 编码，是 JSON Web 令牌 (JSON Web Tokens, JWT) 的一种紧凑二进制替代方案。而 CAT 则在 CWT 的基础上进行了扩展，增加了 URL 模式、IP 限制和 HTTP 方法限制等额外的细粒度访问控制 (fine-grained access control) 功能。这两种令牌类型都使用 [CBOR 对象签名和加密 (CBOR Object Signing and Encryption, COSE)](https://datatracker.ietf.org/doc/html/rfc8152) 来增强安全性，并允许开发人员直接在边缘以亚毫秒级的执行时间实现轻量级、高性能的身份验证机制。

CWT 和 CAT 非常适用于性能关键型应用，例如需要每秒验证数百万次观众访问令牌的直播视频平台，或对带宽效率要求极高的物联网 (IoT) 应用。这些令牌还为跨多 CDN 部署的内容身份验证提供了一种单一、标准化的方法，从而简化了安全管理，并避免了为每个 CDN 提供商进行独特配置的需要。例如，一家媒体公司可以使用 CAT 创建令牌，根据订阅级别、地理位置和设备类型来限制对特定视频内容的访问。所有验证均可在 CloudFront 和其他 CDN 提供商之间保持一致，无需向后端应用发起网络请求。借助 CWT 和 CAT 支持，您可以在 CloudFront Functions 中验证传入的令牌、生成新令牌并实现令牌刷新逻辑。该功能与 CloudFront Functions KeyValueStore 无缝集成，以实现安全的密钥管理。

CloudFront Functions 对 CWT 和 CAT 的支持已在所有 CloudFront 边缘站点提供，无需额外费用。要了解有关 CloudFront Functions CBOR Web 令牌支持的更多信息，请参阅 [Amazon CloudFront 开发人员指南](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cwt-support-cloudfront-functions.html) 。

---

# AWS Site-to-Site VPN 与 eero 合作，简化远程连接

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/site-to-site-vpn-eero-simplify-remote-connectivity/](https://aws.amazon.com/about-aws/whats-new/2025/11/site-to-site-vpn-eero-simplify-remote-connectivity/) 

**发布时间:** 2025-11-20

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Site-to-Site VPN 与 eero 合作，简化远程连接

发布于：2025年11月20日

AWS Site-to-Site VPN 与 eero 展开合作，旨在简化客户将远程站点连接至 AWS 的流程。通过此次合作，客户仅需几次点击，即可在远程站点与 AWS 之间建立安全连接。

许多 AWS 客户运营着数百个远程站点——从餐厅、零售店到加油站和移动办公室。这些站点依赖 WiFi 连接员工、客户以及物联网 (IoT) 应用，例如自助服务终端、自动取款机 (ATM) 和自动售货机，同时还需要连接到 AWS 以进行业务运营。这些客户还需要一种更快速、更高效的方式将数百个站点连接到 AWS。例如，快餐店需要将其每个站点的销售点 (Point of Sales, POS) 系统连接到部署在 AWS 上的支付网关。AWS Site-to-Site VPN 与 eero 正是通过结合 eero 的易用性与 AWS 的网络服务，来简化远程站点的连接性。该解决方案利用 eero 的 WiFi 接入点和网络网关来提供本地连接。通过使用 eero 的网关设备和 AWS Site-to-Site VPN，客户仅需几次点击即可自动建立 VPN 连接，以访问托管在 AWS 上的应用程序，例如用于销售点系统的支付网关。这使得客户能够更简单、更快速地将其远程站点连接扩展到数百个站点，并且无需具备网络专业知识的现场技术人员来设置连接。

客户可以在美国区域使用 eero 设备，通过 Site-to-Site VPN 建立到 AWS 的连接。要了解更多信息并开始使用，请访问 AWS Site-to-Site VPN 文档和 eero [文档](https://support.eero.com/hc/en-us/articles/42827838351899-AWS-Account-and-VPN-Configuration) 。

---

# AWS Site-to-Site VPN 现已支持 VPN 隧道的 BGP 日志记录

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/site-to-site-vpn-bgp-logging-vpn-tunnels/](https://aws.amazon.com/about-aws/whats-new/2025/11/site-to-site-vpn-bgp-logging-vpn-tunnels/) 

**发布时间:** 2025-11-20

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Site-to-Site VPN 现已支持 VPN 隧道的 BGP 日志记录

发布于: 2025年11月20日

AWS Site-to-Site VPN 现已允许客户将来自 VPN 隧道的边界网关协议 (BGP) 日志发布到 AWS CloudWatch，从而增强对 VPN 配置的可见性，并简化连接问题的故障排查。

AWS Site-to-Site VPN 是一项完全托管的服务，它使用 IPSec 隧道在本地数据中心或分支机构与 AWS 资源之间建立安全连接。在此之前，客户只能访问显示 IKE/IPSec 隧道详细信息的隧道活动日志。本次发布后，客户现在可以访问详细的 BGP 日志，从而深入了解 BGP 会话状态和转换、路由更新以及详细的 BGP 错误状态。这些日志有助于识别 AWS VPN 终端节点与客户网关设备之间的配置不匹配问题，为 BGP 相关事件提供精细的可见性。现在，VPN 隧道日志和 BGP 日志都可以在 CloudWatch 中使用，客户可以更轻松地监控和分析其 VPN 连接，从而更快地解决连接问题。

此功能已在所有提供 AWS Site-to-Site VPN 的 AWS 商业区域和 AWS GovCloud (US) 区域上线。要了解更多信息并开始使用，请访问 AWS Site-to-Site VPN [文档](https://docs.aws.amazon.com/vpn/latest/s2svpn/monitoring-logs.html) 。

---

# AWS Cloud WAN 新增路由策略，实现高级流量控制和灵活网络部署

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/aws-cloud-wan-routing-policy/](https://aws.amazon.com/about-aws/whats-new/2025/11/aws-cloud-wan-routing-policy/) 

**发布时间:** 2025-11-20

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Cloud WAN 新增路由策略，实现高级流量控制和灵活网络部署

发布于: 2025 年 11 月 20 日

AWS 宣布 Cloud WAN 路由策略 (Routing Policy) 正式可用，为客户提供精细化控制，以优化其全球广域网 (wide-area networks) 的路由管理、控制流量模式并自定义网络行为。

AWS Cloud WAN 允许您构建、监控和管理一个统一的全球网络，用于互连您在 AWS 云中的资源和本地环境 (on-premises environments)。通过使用新的路由策略功能，客户可以执行路由过滤 (route filtering) 和路由汇总 (summarization) 等高级路由技术，从而更好地控制 AWS Cloud WAN 与外部网络之间交换的路由。该功能使客户能够构建受控的路由环境，以最小化路由可达性的爆炸半径 (blast radius)、防止次优或非对称的连接模式，并避免因不必要的路由在全局网络中传播而导致路由表溢出。此外，该功能还允许客户设置高级边界网关协议 (Border Gateway Protocol, BGP) 属性，以根据其个性化需求自定义网络流量行为，并构建高弹性的混合云 (hybrid-cloud) 网络架构。该功能还在路由数据库中提供了高级可见性，以便在复杂的多路径环境中快速排查网络问题。

新的路由策略功能已在所有提供 AWS Cloud WAN 的 [AWS 区域 (AWS Regions)](https://docs.aws.amazon.com/network-manager/latest/cloudwan/what-is-cloudwan.html#cloudwan-available-regions) 上线。您可以使用 AWS 管理控制台 (AWS Management Console)、AWS 命令行界面 (AWS Command Line Interface, CLI) 和 AWS 软件开发工具包 (AWS Software Development Kit, SDK) 启用这些功能。在 AWS Cloud WAN 上启用路由策略不收取额外费用。更多信息，请参阅 AWS Cloud WAN [文档页面](https://docs.aws.amazon.com/network-manager/latest/cloudwan/what-is-cloudwan.html) 和 [博客](https://aws.amazon.com/blogs/networking-and-content-delivery/aws-cloud-wan-routing-policy-fine-grained-controls-for-your-global-network-part-1/)。

---

# Amazon CloudFront 现已支持与源站建立 TLS 1.3 连接

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-cloudfront-tls13-origin](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-cloudfront-tls13-origin) 

**发布时间:** 2025-11-20

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon CloudFront 现已支持与源站建立 TLS 1.3 连接

发布于: 2025年11月20日

Amazon CloudFront 现已支持在连接到您的源站时使用 TLS 1.3，为源站通信提供了更高的安全性和更优的性能。此次升级提供了更强的加密算法、更低的握手延迟，并为 CloudFront 边缘站点 (edge locations) 与您的源服务器 (origin servers) 之间的数据传输带来了更好的整体安全态势。所有源类型，包括自定义源、Amazon S3 和应用程序负载均衡器 (Application Load Balancers)，都已自动启用 TLS 1.3 支持，您无需进行任何配置更改。

当您的源站支持 TLS 1.3 时，它通过减少握手过程中的往返次数来加快连接建立速度，可将连接性能提升高达 30%。当您的源站支持 TLS 1.3 时，CloudFront 会自动协商使用该版本，同时为尚未升级的源站保留对较低 TLS 版本的向后兼容性。这项增强功能特别适用于需要高安全标准的应用，例如处理敏感数据的金融服务、医疗保健和电子商务平台。

在所有 CloudFront 边缘站点，与源站连接的 TLS 1.3 支持均免费提供。要了解有关 CloudFront 源站 TLS 的更多信息，请参阅 [Amazon CloudFront 开发人员指南](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/secure-connections-supported-ciphers-cloudfront-to-origin.html) 。

---

# AWS Application Load Balancer 现已支持健康检查日志

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/application-load-balancer-health-check-logs/](https://aws.amazon.com/about-aws/whats-new/2025/11/application-load-balancer-health-check-logs/) 

**发布时间:** 2025-11-21

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Application Load Balancer 现已支持健康检查日志

发布于: 2025 年 11 月 21 日

AWS Application Load Balancer (ALB) 现已支持健康检查日志 (Health Check Logs)，允许您将详细的目标健康检查日志数据直接发送到指定的 Amazon S3 存储桶。这项可选功能可以捕获全面的目标健康检查状态、时间戳、目标识别数据以及失败原因。

健康检查日志通过精确的故障诊断，提供了对目标健康状态的完整可见性，使您无需联系 AWS Support 即可更快地进行故障排查。您可以分析目标随时间变化的健康模式，准确判断实例被标记为不健康的原因，并显著缩短目标健康调查的平均解决时间 (mean time to resolution)。日志每 5 分钟自动投递到您的 S3 存储桶，除了标准的 S3 存储成本外，不收取额外费用。

该功能已在所有提供 Application Load Balancer 的 AWS 商业区域 (Commercial Regions)、AWS GovCloud (US) 区域和 AWS 中国区域上线。您可以通过 AWS 管理控制台 (AWS Management Console)、AWS CLI 或使用 AWS SDK 以编程方式启用健康检查日志。请在 [AWS 文档](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-monitoring.html) 中了解更多关于 ALB 健康检查日志的信息。

---

# AWS Application Load Balancer 和 Network Load Balancer 现已支持 TLS 的后量子密钥交换

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/network-load-balancers-post-quantum-key-exchange-tls/](https://aws.amazon.com/about-aws/whats-new/2025/11/network-load-balancers-post-quantum-key-exchange-tls/) 

**发布时间:** 2025-11-21

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Application Load Balancer 和 Network Load Balancer 现已支持 TLS 的后量子密钥交换

发布于: 2025-11-21

AWS 应用程序负载均衡器 (Application Load Balancers, ALB) 和网络负载均衡器 (Network Load Balancers, NLB) 现已为传输层安全 (Transport Layer Security, TLS) 协议提供后量子密钥交换 (post-quantum key exchange) 选项。这项可选功能引入了新的 TLS 安全策略，采用混合后量子密钥协商 (hybrid post-quantum key agreement) 机制，将经典密钥交换算法与后量子密钥封装方法 (post-quantum key encapsulation methods) 相结合，其中包括标准化的基于模块化格的密钥封装机制 (Module-Lattice-Based Key-Encapsulation Mechanism, ML-KEM) 算法。

后量子 TLS (Post-quantum TLS, PQ-TLS) 安全策略可以保护您的传输中数据，抵御潜在的“先采集，后解密” (Harvest Now, Decrypt Later, HNDL) 攻击。这类攻击指的是攻击者在当前收集加密数据，并计划在量子计算 (quantum computing) 能力成熟后对其进行解密。这种抗量子加密 (quantum-resistant encryption) 技术可确保您的应用程序和数据传输的长期安全，使您的基础设施能够从容应对新兴的量子计算威胁。

该功能已在所有 AWS 商业区域、AWS GovCloud (美国) 区域和 AWS 中国区域的 ALB 和 NLB 上线，无需额外费用。要使用此功能，您必须通过 AWS 管理控制台 (AWS Management Console)、CLI、API 或 SDK，显式更新您现有的 ALB HTTPS 侦听器或 NLB TLS 侦听器以使用 PQ-TLS 安全策略，或在创建新侦听器时选择 PQ-TLS 策略。您可以使用 ALB 连接日志或 NLB 访问日志来监控经典密钥交换或抗量子密钥交换的使用情况。

更多信息，请访问 [ALB 用户指南](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/describe-ssl-policies.html) 、[NLB 用户指南](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/describe-ssl-policies.html) 和 [AWS 后量子密码学](https://aws.amazon.com/security/post-quantum-cryptography/) 文档。

---

# AWS Network Firewall 现已支持通过 Transit Gateway 实现灵活的成本分摊

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/network-firewall-flexible-cost-allocation/](https://aws.amazon.com/about-aws/whats-new/2025/11/network-firewall-flexible-cost-allocation/) 

**发布时间:** 2025-11-21

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Network Firewall 现已支持通过 Transit Gateway 实现灵活的成本分摊

发布于: 2025年11月21日

[AWS Network Firewall](https://aws.amazon.com/network-firewall/) 现已通过 [AWS Transit Gateway](https://aws.amazon.com/transit-gateway/) 的原生附件 (native attachments) 支持灵活的成本分摊 (flexible cost allocation)，使您能够自动将数据处理成本分配到不同的 AWS 账户。客户可以创建计量策略 (metering policies)，根据其组织的内部成本分摊要求来应用数据处理费用，而无需将所有费用都整合到防火墙所有者账户中。

此功能通过将费用根据实际使用情况分配给应用程序团队，帮助安全和网络团队更好地管理集中式防火墙成本。组织现在可以保持集中式安全控制，同时自动将检测成本分配给相应的业务部门或应用程序所有者，从而无需使用自定义成本管理解决方案。

灵活的成本分摊功能已在所有支持 AWS Network Firewall 和 Transit Gateway 附件的 [AWS 商业区域](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) 和亚马逊中国区域上线。

除了 [AWS Network Firewall](https://aws.amazon.com/network-firewall/pricing/) 和 [AWS Transit Gateway](https://aws.amazon.com/transit-gateway/pricing/) 的标准定价外，使用此附件或灵活的成本分摊功能不会产生额外费用。

要了解更多信息，请访问 AWS Network Firewall 服务[文档](https://docs.aws.amazon.com/network-firewall/latest/developerguide/firewall-creating.html) 。

---

# Amazon Lightsail 扩展蓝图选择，新增对 Nginx 蓝图的支持

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/announcing-nginx-blueprint-by-amazon-lightsail/](https://aws.amazon.com/about-aws/whats-new/2025/11/announcing-nginx-blueprint-by-amazon-lightsail/) 

**发布时间:** 2025-11-21

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon Lightsail 扩展蓝图选择，新增对 Nginx 蓝图的支持

发布于：2025 年 11 月 21 日

Amazon Lightsail 现已提供全新的 Nginx 蓝图 (blueprint)。这款新蓝图默认强制启用实例元数据服务版本 2 (Instance Metadata Service Version 2, IMDSv2)，并支持纯 IPv6 实例。只需点击几下，您就可以创建一台预装了 Nginx 且大小合意的 Lightsail 虚拟私有服务器 (virtual private server, VPS)。

借助 Lightsail，您可以通过选择蓝图和实例套餐 (instance bundle) 来构建您的 Web 应用程序，轻松开启云上之旅。Lightsail 实例套餐包含预装了您首选操作系统、存储和每月数据传输限额的实例，为您提供了快速启动和运行所需的一切。

这款新蓝图现已在所有提供 Lightsail 服务的 [AWS 区域](https://docs.aws.amazon.com/en_us/lightsail/latest/userguide/understanding-regions-and-availability-zones-in-amazon-lightsail.html) 上线。有关 Lightsail 支持的蓝图的更多信息，请参阅 [Lightsail 文档](https://lightsail.aws.amazon.com/ls/docs/en_us/articles/compare-options-choose-lightsail-instance-image)。有关定价的更多信息或开始免费试用，请[点击此处](https://aws.amazon.com/lightsail/pricing/)。

---

# 第二代 AWS Outposts 机架现已在 AWS 亚太地区 (东京) 区域提供支持

发布于: 2025年11月21日

第二代 AWS Outposts 机架 (racks) 现已在 AWS 亚太地区 (东京) 区域提供支持。Outposts 机架将 AWS 基础设施、AWS 服务、API 和工具扩展到几乎任何本地数据中心 (on-premises data center) 或主机托管空间 (colocation space)，以提供真正一致的混合体验。

从初创公司到企业和公共部门，日本内外的各类组织现在都可以订购连接到这个新增支持区域的 Outposts 机架，以优化其延迟 (latency) 和数据驻留 (data residency) 需求。Outposts 允许客户在本地运行需要低延迟访问本地系统的工作负载，同时连接回其主区域 (home Region) 进行应用程序管理。客户还可以使用 Outposts 和 AWS 服务来管理和处理那些为满足数据驻留要求而需要保留在本地的数据。此次区域扩展为客户的 Outposts 可以连接的 AWS 区域提供了更大的灵活性。

要了解有关第二代 Outposts 机架的更多信息，请阅读 [*这篇博客文章*](https://aws.amazon.com/blogs/aws/announcing-second-generation-aws-outposts-racks-with-breakthrough-performance-and-scalability-on-premises/) 和 [*用户指南*](https://docs.aws.amazon.com/outposts/latest/network-userguide/what-is-outposts.html) 。要获取支持第二代 Outposts 机架的国家、地区以及 AWS 区域的最新列表，请查看 [*Outposts 机架常见问题页面*](https://aws.amazon.com/outposts/rack/faqs/) 。

---

# Amazon Route 53 DNS 服务新增对 IPv6 API 服务终端节点的支持

发布于：2025 年 11 月 21 日

即日起，Amazon Route 53 的 DNS 服务 API 终端节点 `route53.global.api.aws` 开始支持双栈 (dual stack)，允许您通过互联网协议第 6 版 (IPv6)、互联网协议第 4 版 (IPv4) 或双栈客户端进行连接。现有的 Route 53 DNS 服务 IPv4 API 终端节点将继续保留，以实现向后兼容性。

Amazon Route 53 是一项高可用、可扩展的域名系统 (DNS) Web 服务，客户可以利用它注册域名、设置与基础设施对应的 DNS 记录、使用 Traffic Flow 进行全局流量路由，并通过 Route 53 运行状况检查来监控应用程序和资源的健康状况与性能。随着互联网的持续发展，IPv4 地址空间正逐步耗尽，客户正在向 IPv6 地址过渡。现在，客户端可以通过 IPv6 连接到 Route 53 DNS 服务的 API 终端节点，这有助于企业满足合规性要求，并消除了在 IPv4 和 IPv6 之间进行 IP 地址转换的额外复杂性。

Route 53 DNS 服务 API 终端节点对 IPv6 的支持已在所有商业区域推出，无需额外费用。您可以通过 AWS CLI 或 [AWS 管理控制台 (AWS Management Console)](https://console.aws.amazon.com/rds/home) 开始使用此功能。要了解哪些 Route 53 功能可通过 `route53.amazon.aws` 服务终端节点访问，请访问[此页面](https://docs.aws.amazon.com/general/latest/gr/r53.html) ；要了解有关 Route 53 DNS 服务的更多信息，请访问我们的[文档](https://docs.aws.amazon.com/Route53/latest/APIReference/Welcome.html) 。

---

# AWS 宣布在 AWS Transit Gateway 上推出灵活成本分配功能

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/aws-transit-gateway-flexible-cost-allocation/](https://aws.amazon.com/about-aws/whats-new/2025/11/aws-transit-gateway-flexible-cost-allocation/) 

**发布时间:** 2025-11-21

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS 宣布在 AWS Transit Gateway 上推出灵活成本分配功能

发布于: 2025 年 11 月 21 日

AWS 宣布 AWS Transit Gateway 的灵活成本分配 (Flexible Cost Allocation) 功能正式发布，该功能增强了您在整个组织内部分配 Transit Gateway 成本的方式。

此前，Transit Gateway 仅使用发送方付费模式，即源附件账户所有者负责所有与数据使用相关的成本。新的灵活成本分配 (FCA) 功能通过中央计量策略提供了更灵活的成本分配选项。通过使用 FCA 计量策略，您可以选择将所有 Transit Gateway 数据处理和数据传输使用量分配给源附件账户、目标附件账户或中央 Transit Gateway 账户。FCA 计量策略可以在附件级别或单个流级别的粒度上进行配置。FCA 还支持中间盒部署模型，使您能够将 AWS Network Firewall 等中间盒设备上的数据处理使用量分配给原始的源或目标附件所有者。这种灵活性使您可以在单个 Transit Gateway 上实施多种成本分配模型，以适应您 AWS 网络基础设施中的各种成本分摊场景。

灵活成本分配功能已在所有提供 Transit Gateway 的商用 AWS 区域 (AWS Regions) 上线。您可以使用 AWS 管理控制台 (AWS Management Console)、AWS 命令行界面 (CLI) 和 AWS 软件开发工具包 (SDK) 来启用这些功能。在 Transit Gateway 上使用 FCA 不会产生额外费用。要了解更多信息，请参阅 Transit Gateway [文档页面。](https://docs.aws.amazon.com/vpc/latest/tgw/metering-policy.html)

---

# Amazon API Gateway REST API 现已支持与 Application Load Balancer 的私有集成

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/api-gateway-rest-apis-integration-load-balancer/](https://aws.amazon.com/about-aws/whats-new/2025/11/api-gateway-rest-apis-integration-load-balancer/) 

**发布时间:** 2025-11-21

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon API Gateway REST API 现已支持与 Application Load Balancer 的私有集成

发布于: 2025 年 11 月 21 日

Amazon API Gateway REST API 现已支持与应用程序负载均衡器 (Application Load Balancer, ALB) 的直接私有集成，从而实现了到内部 ALB 的 VPC 间连接。此项增强功能扩展了 API Gateway 现有的 VPC 连接能力，为您的 REST API 实现提供了更灵活、更高效的架构选择。

这种直接的 ALB 集成带来了多项优势：通过消除先前通过网络负载均衡器 (Network Load Balancer) 所需的额外网络跳数来降低延迟，通过简化的架构降低基础设施成本，并增强了第 7 层 (Layer 7) 功能，包括 HTTP/HTTPS 健康检查、基于请求的高级路由以及原生容器服务集成。您仍然可以使用 API Gateway 与网络负载均衡器的集成来实现第 4 层 (Layer 4) 的连接。

Amazon API Gateway 与 ALB 的私有集成已在所有 AWS GovCloud (US) 区域以及以下 AWS 商业区域推出：美国东部 (弗吉尼亚北部)、美国东部 (俄亥俄)、美国西部 (加利福尼亚北部)、美国西部 (俄勒冈)、非洲 (开普敦)、亚太地区 (香港)、亚太地区 (海得拉巴)、亚太地区 (雅加达)、亚太地区 (马来西亚)、亚太地区 (墨尔本)、亚太地区 (孟买)、亚太地区 (大阪)、亚太地区 (首尔)、亚太地区 (新加坡)、亚太地区 (悉尼)、亚太地区 (东京)、加拿大 (中部)、加拿大西部 (卡尔加里)、欧洲 (法兰克福)、欧洲 (爱尔兰)、欧洲 (伦敦)、欧洲 (米兰)、欧洲 (巴黎)、欧洲 (西班牙)、欧洲 (斯德哥尔摩)、欧洲 (苏黎世)、以色列 (特拉维夫)、中东 (巴林)、中东 (阿联酋)、南美洲 (圣保罗)。欲了解更多信息，请访问 [Amazon API Gateway 文档](https://docs.aws.amazon.com/apigateway/latest/developerguide/private-integration.html) 和 [博客文章](https://aws.amazon.com/blogs/compute/build-scalable-rest-apis-using-amazon-api-gateway-private-integration-with-application-load-balancer/) 。

---

# Amazon CloudFront 宣布支持双向 TLS 认证

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-cloudfront-mutual-tls-authentication/](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-cloudfront-mutual-tls-authentication/) 

**发布时间:** 2025-11-24

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon CloudFront 宣布支持双向 TLS 认证

发布于: 2025 年 11 月 24 日

Amazon CloudFront 宣布支持双向 TLS 认证 (mutual TLS Authentication, mTLS)，这是一种安全协议，要求服务器和客户端使用 X.509 证书相互认证，使客户能够在 CloudFront 的边缘站点 (edge locations) 验证客户端身份。现在，客户可以确保只有持有受信任证书的客户端才能访问其分发 (distributions)，从而帮助防范未经授权的访问和安全威胁。

以往，客户需要持续投入精力来实施和维护自己的客户端访问管理解决方案，这带来了无差异化的繁重工作 (undifferentiated heavy lifting)。现在，借助对双向 TLS 的支持，客户可以在与应用程序服务器或 API 建立连接之前，在 AWS 边缘轻松验证客户端身份。典型用例包括企业的 B2B 安全 API 集成和物联网 (IoT) 的客户端身份验证。在 B2B API 安全方面，企业可以使用双向 TLS 认证来自受信任的第三方和合作伙伴的 API 请求。在物联网用例中，企业可以验证设备是否有权接收固件更新等专有内容。客户可以利用其现有的第三方证书颁发机构 (Certificate Authorities) 或 [AWS Private Certificate Authority](https://docs.aws.amazon.com/privateca/latest/userguide/PcaWelcome.html) 来签署 X.509 证书。通过双向 TLS，客户可以为需要客户端身份验证的工作负载获得 CloudFront 的性能和规模优势。

双向 TLS 认证功能向所有 CloudFront 客户提供，无需额外费用。客户可以使用 AWS 管理控制台 (AWS Management Console)、CLI、SDK、CDK 和 CloudFormation 来为 CloudFront 配置双向 TLS。有关详细的实施指南和最佳实践，请访问 [CloudFront 双向 TLS (查看器) 文档](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/mtls-authentication.html) 。

---

# Amazon CloudFront 集成 VPC IPAM 以支持 BYOIP

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/vpc-ipam-cloudfront-byoip](https://aws.amazon.com/about-aws/whats-new/2025/11/vpc-ipam-cloudfront-byoip) 

**发布时间:** 2025-11-24

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon CloudFront 集成 VPC IPAM 以支持 BYOIP

发布于: 2025 年 11 月 24 日

Amazon CloudFront 现已通过 VPC IP 地址管理器 (IPAM) 支持为任播静态 IP (Anycast Static IPs) 使用自有 IP 地址 (BYOIP)。该功能使网络管理员能够将自己的公有 IPv4 地址池用于 CloudFront 分配，从而简化了在 AWS 全球基础设施上的 IP 地址管理。

CloudFront 通常使用轮换的 IP 地址来提供流量服务。CloudFront 任播静态 IP 功能允许客户向合作伙伴和客户提供专用的 IP 地址列表，从而增强安全性并简化网络管理。此前，使用任播静态 IP 的客户会为其工作负载获得由 AWS 提供的静态 IP 地址。借助 IPAM 的统一界面，客户现在可以使用 BYOIP 创建专用的 IP 地址池，并将其分配给 CloudFront 任播静态 IP 列表。客户在迁移到 CloudFront 时无需更改其应用程序的现有 IP 地址空间，从而可以保留现有的允许列表和品牌形象。

该功能已在所有商业 AWS 区域 (AWS Regions) 的 Amazon VPC IPAM 中提供，但不包括 AWS GovCloud (美国) 区域以及中国 (北京，由光环新网运营) 和中国 (宁夏，由西云数据运营) 区域。要了解有关 CloudFront BYOIP 功能的更多信息，请查看 [BYOIP CloudFront 文档](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/bring-your-own-ip-address-using-ipam.html) 。有关定价详情，请参阅 [Amazon VPC 定价页面](https://aws.amazon.com/vpc/pricing/) 上的 IPAM 标签页。

---

# Amazon Route 53 宣布推出用于管理公有 DNS 记录的加速恢复功能

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-route-53-accelerated-recovery-managing-public-dns-records](https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-route-53-accelerated-recovery-managing-public-dns-records) 

**发布时间:** 2025-11-26

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon Route 53 宣布推出用于管理公有 DNS 记录的加速恢复功能
发布于: 2025年11月26日
Amazon Route 53 很高兴发布用于管理公有托管区域 (public hosted zones) 中 DNS 记录的加速恢复选项。如果美国东部 (弗吉尼亚北部) 区域的 AWS 服务暂时不可用，加速恢复功能旨在实现 60 分钟的恢复时间目标 (Recovery Time Objective, RTO)，以重新获得在 Route 53 公有托管区域中更改 DNS 记录的能力。
如今，客户使用 Route 53 公有 DNS 服务的 API 来更改 DNS 记录，以支持软件部署、运行基础设施运维和接纳新用户。银行、金融科技 (FinTech) 和软件即服务 (SaaS) 等行业的客户尤其需要一个可预测的、较短的 RTO，以满足其业务连续性和灾难恢复 (disaster recovery) 的目标。过去，如果美国东部 (弗吉尼亚北部) 区域的 AWS 服务不可用，客户将无法修改或重新创建 DNS 记录，以将用户和内部服务指向更新后的端点。现在，当您在 Route 53 公有托管区域上启用加速恢复选项后，一旦发生此类中断，您很快就能在该托管区域中更改 Route 53 公有 DNS 记录 (资源记录集, Resource Record Sets)，通常耗时不到一小时。
用于管理公有 DNS 记录的加速恢复功能已在全球范围上线，但在 AWS GovCloud 和亚马逊云科技中国区域除外。使用此功能不收取额外费用。要了解有关加速恢复选项的更多信息，请访问我们的[文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/accelerated-recovery.html) 。

---

# 隆重推出 Amazon Route 53 全局解析器 (Global Resolver)，实现安全的任播 (anycast) DNS 解析 (预览版)
发布于：2025 年 11 月 30 日

今天，AWS 宣布推出 Amazon Route 53 全局解析器 (Global Resolver) 的预览版。这是一款可通过互联网访问的新型 DNS 解析器 (DNS resolver)，能为来自任何地方的授权客户端 (authorized clients) 查询提供简单、安全且可靠的 DNS 解析。

借助全局解析器，您组织内的授权客户端可以从任何地方解析互联网上的公有域和与 Route 53 私有托管区 (private hosted zones) 关联的私有域，从而实现分离 DNS (split DNS) 解析。全局解析器还允许您创建规则来保护客户端免受基于 DNS 的数据泄露攻击。通过为全局解析器配置 DNS 防火墙 (DNS Firewall) 规则，您可以根据威胁类别 (例如恶意软件、垃圾邮件)、网页内容 (例如成人及不适宜内容、赌博) 或高级 DNS 威胁 (例如 DNS 隧道 (DNS tunneling)、域名生成算法 (Domain Generation Algorithms)) 来过滤域名查询，并集中记录所有查询以便于审计。全局解析器允许您选择两个或更多区域进行任播 DNS 解析，并具备到最近可用区域的自动故障切换 (automatic failover) 功能，从而为您的客户端实现 DNS 解析的高可用性。

随着全局解析器的发布，我们将 Route 53 Resolver 更名为 [Route 53 VPC 解析器 (VPC Resolver)](https://aws.amazon.com/route53/vpc-resolver/) ，以帮助阐明两种服务之间的区别。Route 53 VPC 解析器允许您解析来自 Amazon VPC 中 AWS 资源的 DNS 查询，这些查询可以针对公有域名、VPC 特定的 DNS 名称以及 Amazon Route 53 私有托管区，并且默认在每个 VPC 中可用。您还可以将解析器终端节点 (Resolver endpoints) 与 VPC 解析器关联，以便在您的本地 (on-premises) 环境和 Amazon VPC 之间转发 DNS 查询。

请访问 [服务页面](https://aws.amazon.com/route53/global-resolver/) 查看全局解析器的定价和功能详情。在预览期间，全局解析器将免费提供。有关预览期间支持全局解析器的 AWS 区域的更多信息，请参阅 [此文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/gr-what-is-global-resolver.html) 。如需获取分步入门指南，请参阅 [AWS 新闻博客](https://aws.amazon.com/blogs/aws/introducing-amazon-route-53-global-resolver-for-secure-anycast-dns-resolution-preview/) 或 [官方文档](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/gr-what-is-global-resolver.html) 。

---

# AWS 宣布推出 AWS Interconnect - multicloud 预览版

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/preview-aws-interconnect-multicloud/](https://aws.amazon.com/about-aws/whats-new/2025/11/preview-aws-interconnect-multicloud/) 

**发布时间:** 2025-11-30

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS 宣布推出 AWS Interconnect - multicloud 预览版

发布于: 2025 年 11 月 30 日

AWS 宣布推出 AWS Interconnect - multicloud 预览版，该服务可提供与其他云服务提供商 (Cloud Service Providers, CSP) 之间的简单、有弹性且高速的私有连接。预览版将首先与 Google Cloud 合作推出，并计划于 2026 年晚些时候支持 Microsoft Azure。

在将更多应用程序迁移到云端的同时，客户一直在采纳多云 (multicloud) 策略。客户这样做是出于多种原因，包括满足互操作性 (interoperability) 要求、自由选择最适合其需求的技术，以及在任何环境中更轻松、更快速地构建和部署应用程序的能力。以往，当客户需要跨多个云提供商互连工作负载 (workloads) 时，他们不得不采用“自己动手” (do-it-yourself) 的多云方法，这导致了大规模管理全球多层网络的复杂性。AWS Interconnect - multicloud 是首款此类专用产品，它提供了一种全新的云间连接和通信方式。它使客户能够在他们的 Amazon VPC 和其他云环境之间，快速建立具有专用带宽和内置弹性的私有、安全、高速的网络连接。通过 Interconnect - multicloud，客户可以轻松地将 AWS Transit Gateway、AWS Cloud WAN 和 Amazon VPC 等 AWS 网络服务快速连接到其他 CSP，整个过程只需很短时间，而不再是数周或数月。

Interconnect - multicloud 预览版已在五个 AWS 区域 (Regions) 提供。您可以使用 AWS 管理控制台 (AWS Management Console) 启用此功能。CSP 也可以通过 GitHub 上发布的开放 API (open API) 包轻松接入。有关更多信息，请参阅 AWS Interconnect - multicloud 文档页面。

---

# AWS 宣布推出 AWS Interconnect - last mile 的门控预览版

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/11/gated-preview-interconnect-last-mile/](https://aws.amazon.com/about-aws/whats-new/2025/11/gated-preview-interconnect-last-mile/) 

**发布时间:** 2025-11-30

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS 宣布推出 AWS Interconnect - last mile 的门控预览版

发布于: 2025-11-30

AWS 推出了 AWS Interconnect - last mile，这是一款完全托管的连接产品，允许客户仅需几次点击即可将其分支机构、数据中心和远程位置连接到 AWS，消除了寻找合作伙伴的繁琐流程和网络设置的复杂性。作为 AWS 与 Lumen 之间里程碑式的合作，AWS Interconnect - last mile 结合了 AWS 的云创新能力与 Lumen 广泛的网络覆盖范围，重新定义了企业连接到云的方式。

现在，客户只需输入其位置、选择带宽并指定 AWS 区域 (AWS Region)，即可即时建立到 AWS 的私有高速连接。该服务的推出通过自动化复杂的网络配置，包括 BGP 对等 (BGP peering)、VLAN 配置和 ASN 分配，简化了连接体验。客户可以通过 AWS 管理控制台 (AWS console) 动态扩展 1 Gbps 到 100 Gbps 的带宽，并享受零停机维护带来的便利。该服务专为高可用性 (high availability) 而设计，并提供服务等级协议 (SLAs) 保障。默认启用 MACsec 加密，以增强 AWS Direct Connect 和合作伙伴设备之间的安全性。

从即日起，AWS Interconnect - last mile 通过我们的首发合作伙伴 Lumen，以门控预览版的形式向美国客户提供。请在此处 [申请访问](https://aws.amazon.com/interconnect/lastmile) 。

---

# Amazon API Gateway 新增 MCP 代理支持

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/12/api-gateway-mcp-proxy-support/](https://aws.amazon.com/about-aws/whats-new/2025/12/api-gateway-mcp-proxy-support/) 

**发布时间:** 2025-12-02

**厂商:** AWS

**类型:** WHATSNEW

---
# Amazon API Gateway 新增 MCP 代理支持
发布于：2025年12月2日

Amazon API Gateway 现已支持模型上下文协议 (Model Context Protocol, MCP) 代理，允许您将现有的 REST API 转换为与 MCP 兼容的端点。这项新功能使组织能够将其 API 开放给 AI 智能体 (AI agents) 和 MCP 客户端。通过与 Amazon Bedrock AgentCore 的网关服务集成，您可以安全地将 REST API 转换为与智能体兼容的工具，同时通过语义搜索 (semantic search) 实现智能工具发现。

MCP 代理功能与 Bedrock AgentCore 网关服务相结合，提供了三大核心优势。首先，它通过协议转换 (protocol translation) 使 REST API 能够与 AI 智能体和 MCP 客户端通信，无需修改应用程序或管理额外的基础设施。其次，它通过双重身份验证 (dual authentication) 提供全面的安全性——既能验证入站请求的智能体身份，又能管理到 REST API 的出站调用的安全连接。最后，它使 AI 智能体能够搜索并选择与提示词上下文 (prompt context) 最匹配的 REST API。

要了解此功能的定价信息，请参阅 [Amazon Bedrock AgentCore 定价页面。 ](https://aws.amazon.com/bedrock/agentcore/pricing/) Amazon API Gateway MCP 代理功能已在 Amazon Bedrock AgentCore 上线的九个 AWS 区域提供：亚太地区 (孟买)、亚太地区 (新加坡)、亚太地区 (悉尼)、亚太地区 (东京)、欧洲 (都柏林)、欧洲 (法兰克福)、美国东部 (弗吉尼亚北部)、美国东部 (俄亥俄) 和美国西部 (俄勒冈)。要开始使用，请访问 [Amazon API Gateway 文档](https://docs.aws.amazon.com/apigateway/latest/developerguide/mcp-server.html)。

---

# AWS Shield network security director 现已支持多账户分析

**原始链接:** [https://aws.amazon.com/about-aws/whats-new/2025/12/aws-shield-network-security-director-multi-account-analysis](https://aws.amazon.com/about-aws/whats-new/2025/12/aws-shield-network-security-director-multi-account-analysis) 

**发布时间:** 2025-12-12

**厂商:** AWS

**类型:** WHATSNEW

---
# AWS Shield network security director 现已支持多账户分析

发布于: 2025-12-12

今天，AWS Shield 宣布其 network security director 功能现已支持多账户网络安全管理和自动化网络分析，该功能目前处于预览版 (preview) 阶段。AWS Shield network security director 提供了对您 AWS Organization 中 AWS 资源的可见性 (visibility)，能够识别缺失或配置错误的网络安全服务，并推荐修复步骤。

通过 network security director，您可以指定一个委派的管理员账户 (delegated administrator account)，并以此为起点，对 AWS Organization 中的多个账户或组织单元 (organizational units) 启动持续的网络分析。之后，您可以集中查看每个账户的网络拓扑 (network topology)、网络安全检测结果 (network security findings) 以及针对缺失或配置错误的网络安全服务的建议修复措施。您还可以在 AWS Management Console 和聊天应用程序中，通过 Amazon Q Developer 轻松地对 AWS Shield network security director 识别出的网络安全配置错误进行汇总和报告。

AWS Shield network security director 现已在另外五个 AWS 区域 (AWS regions) 上线：欧洲 (爱尔兰)、欧洲 (法兰克福)、亚太地区 (香港)、亚太地区 (新加坡) 和澳大利亚 (悉尼)。

要了解更多信息，请访问 [*概述*](https://aws.amazon.com/shield/) 页面。
