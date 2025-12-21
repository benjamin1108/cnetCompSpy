# VPC Lattice 2025年更新合集

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



# Amazon VPC Lattice 现已支持为资源网关配置 IP 地址

发布于: 2025 年 10 月 7 日

即日起，Amazon VPC Lattice 允许您为资源网关 (Resource Gateway) 的弹性网络接口 (ENIs) 配置分配的 IPv4 地址数量。这项增强功能建立在 VPC Lattice 的现有能力之上，即跨多个 VPC 和账户提供对第 4 层 (Layer-4) 资源的访问，例如数据库、集群、域名等。

在配置资源网关时，您现在可以为每个 ENI 指定 IPv4 地址的数量，该设置一旦配置便不可更改。这些 IPv4 地址用于网络地址转换 (Network Address Translation)，并决定了到单个资源的最大并发 IPv4 连接数。在配置 IPv4 地址数量时，您应充分考虑预期的连接量。默认情况下，VPC Lattice 会为每个 ENI 分配 16 个 IPv4 地址。对于 IPv6，VPC Lattice 始终为每个 ENI 分配一个 /80 CIDR。

此功能已在所有提供 VPC Lattice 的 AWS 区域 (AWS Regions) 推出，无需额外费用。要了解更多信息，请访问 [Amazon VPC Lattice 产品详情页面](https://aws.amazon.com/vpc/lattice/) 和 [Amazon VPC Lattice 文档](https://docs.aws.amazon.com/vpc-lattice/latest/ug/resource-gateway.html#ipv4-address-type-per-eni)。

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

