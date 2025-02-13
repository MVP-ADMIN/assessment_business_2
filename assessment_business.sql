/*
 Navicat Premium Data Transfer

 Source Server         : user
 Source Server Type    : MySQL
 Source Server Version : 50744
 Source Host           : localhost:3307
 Source Schema         : assessment_business

 Target Server Type    : MySQL
 Target Server Version : 50744
 File Encoding         : 65001

 Date: 13/02/2025 11:58:27
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for accounts
-- ----------------------------
DROP TABLE IF EXISTS `accounts`;
CREATE TABLE `accounts`  (
  `account_id` int(11) NOT NULL AUTO_INCREMENT,
  `account_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`account_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of accounts
-- ----------------------------
INSERT INTO `accounts` VALUES (1, '账号A');
INSERT INTO `accounts` VALUES (2, '账号B');
INSERT INTO `accounts` VALUES (3, '账号C');
INSERT INTO `accounts` VALUES (4, '账号A');
INSERT INTO `accounts` VALUES (5, '账号B');
INSERT INTO `accounts` VALUES (6, '账号C');

-- ----------------------------
-- Table structure for ad_entry_options
-- ----------------------------
DROP TABLE IF EXISTS `ad_entry_options`;
CREATE TABLE `ad_entry_options`  (
  `option_id` int(11) NOT NULL AUTO_INCREMENT,
  `option_name` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`option_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of ad_entry_options
-- ----------------------------
INSERT INTO `ad_entry_options` VALUES (1, '是');
INSERT INTO `ad_entry_options` VALUES (2, '否');

-- ----------------------------
-- Table structure for brands
-- ----------------------------
DROP TABLE IF EXISTS `brands`;
CREATE TABLE `brands`  (
  `brand_id` int(11) NOT NULL AUTO_INCREMENT,
  `brand_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`brand_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of brands
-- ----------------------------
INSERT INTO `brands` VALUES (1, '品牌A');
INSERT INTO `brands` VALUES (2, '品牌B');
INSERT INTO `brands` VALUES (3, '品牌C');
INSERT INTO `brands` VALUES (4, '品牌A');
INSERT INTO `brands` VALUES (5, '品牌B');
INSERT INTO `brands` VALUES (6, '品牌C');

-- ----------------------------
-- Table structure for business_types
-- ----------------------------
DROP TABLE IF EXISTS `business_types`;
CREATE TABLE `business_types`  (
  `type_id` int(11) NOT NULL AUTO_INCREMENT,
  `type_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`type_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of business_types
-- ----------------------------
INSERT INTO `business_types` VALUES (1, '联营');
INSERT INTO `business_types` VALUES (2, '自营');

-- ----------------------------
-- Table structure for change_logs
-- ----------------------------
DROP TABLE IF EXISTS `change_logs`;
CREATE TABLE `change_logs`  (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `demand_id` int(11) NOT NULL,
  `change_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `change_description` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `old_status_id` int(11) NULL DEFAULT NULL,
  `new_status_id` int(11) NULL DEFAULT NULL,
  PRIMARY KEY (`log_id`) USING BTREE,
  INDEX `demand_id`(`demand_id`) USING BTREE,
  INDEX `old_status_id`(`old_status_id`) USING BTREE,
  INDEX `new_status_id`(`new_status_id`) USING BTREE,
  CONSTRAINT `change_logs_ibfk_1` FOREIGN KEY (`demand_id`) REFERENCES `demands` (`demand_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `change_logs_ibfk_2` FOREIGN KEY (`old_status_id`) REFERENCES `demand_status` (`status_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `change_logs_ibfk_3` FOREIGN KEY (`new_status_id`) REFERENCES `demand_status` (`status_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of change_logs
-- ----------------------------
INSERT INTO `change_logs` VALUES (1, 1, '2025-02-12 12:29:22', '暂停原因: 技术暂停', 1, 2);
INSERT INTO `change_logs` VALUES (2, 1, '2025-02-12 12:29:27', '继续执行原因: 继续', 2, 1);
INSERT INTO `change_logs` VALUES (3, 1, '2025-02-12 12:29:51', '暂停原因: 暂停', 1, 2);
INSERT INTO `change_logs` VALUES (4, 1, '2025-02-12 12:30:00', '继续执行原因: 继续', 2, 1);
INSERT INTO `change_logs` VALUES (5, 1, '2025-02-12 12:31:54', '暂停原因: 1', 1, 2);
INSERT INTO `change_logs` VALUES (6, 1, '2025-02-12 13:16:35', '继续执行原因: 继续', 2, 1);
INSERT INTO `change_logs` VALUES (7, 2, '2025-02-12 13:45:06', '暂停原因: 1', 1, 2);
INSERT INTO `change_logs` VALUES (8, 2, '2025-02-12 15:06:49', '继续执行原因: 010', 2, 1);

-- ----------------------------
-- Table structure for countries
-- ----------------------------
DROP TABLE IF EXISTS `countries`;
CREATE TABLE `countries`  (
  `country_id` int(11) NOT NULL AUTO_INCREMENT,
  `country_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`country_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of countries
-- ----------------------------
INSERT INTO `countries` VALUES (1, '美国');
INSERT INTO `countries` VALUES (2, '英国');
INSERT INTO `countries` VALUES (3, '日本');
INSERT INTO `countries` VALUES (4, '美国');
INSERT INTO `countries` VALUES (5, '英国');
INSERT INTO `countries` VALUES (6, '日本');

-- ----------------------------
-- Table structure for demand_details
-- ----------------------------
DROP TABLE IF EXISTS `demand_details`;
CREATE TABLE `demand_details`  (
  `detail_id` int(11) NOT NULL AUTO_INCREMENT,
  `demand_id` int(11) NOT NULL,
  `order_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `order_amount` decimal(10, 2) NOT NULL,
  `order_time` datetime NOT NULL,
  `review_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `review_time` datetime NULL DEFAULT NULL,
  `review_images` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `review_video` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '评论视频URL',
  `payment_screenshot` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `order_screenshot` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `review_screenshot` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `status` int(11) NOT NULL DEFAULT 1 COMMENT '1:待评论 2:已评论 3:已完成',
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`detail_id`) USING BTREE,
  INDEX `demand_id`(`demand_id`) USING BTREE,
  CONSTRAINT `demand_details_ibfk_1` FOREIGN KEY (`demand_id`) REFERENCES `demands` (`demand_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of demand_details
-- ----------------------------
INSERT INTO `demand_details` VALUES (1, 1, '213123', 0.40, '2025-01-08 00:00:00', '123123', NULL, '', '', '/uploads/1035a3bc-662c-4ff7-b1ba-6032ea2e6865_empty.png', '/uploads/0e102214-88a3-4d4b-998a-613e67e84ba7_O1CN01d4KBlI22wmV8bl7qW__2263287185-2-1-1-1-1-1.jpg', '/uploads/b93f918c-8ea9-4347-9a5e-9f8d8db1dd25_O1CN01d4KBlI22wmV8bl7qW__2263287185-2-1-1-1-1-1.jpg', 1, '', '2025-02-12 11:23:04', '2025-02-12 11:23:04');
INSERT INTO `demand_details` VALUES (2, 1, '123123123123', 0.40, '2025-02-13 00:00:00', '213123123', NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, '2025-02-12 11:28:00', '2025-02-12 11:28:00');
INSERT INTO `demand_details` VALUES (3, 2, '1231231231', 111.00, '2025-02-12 06:09:13', '', '2025-02-12 06:09:14', '', '/uploads/78738eb1-0bee-437c-99e8-9dff4d9ada71_APC244.mp4', '/uploads/1c82a8e1-2a82-473f-8c76-ee5513128ab4_fe2a03ef-9123-4d65-b131-b31a1373da69.png', '/uploads/1b8b681f-75dd-43b9-864b-0968db333f1d_c3d5e180-9123-4474-92ac-e9ec0e23ebc2.png', '/uploads/741062d4-6bbd-4cd7-9ec3-bc66314fbe27_Untitled_1.png', 2, NULL, '2025-02-12 14:10:44', '2025-02-12 15:04:57');
INSERT INTO `demand_details` VALUES (4, 2, '123123123111', 1111.00, '2025-02-11 22:44:44', '1231231111', '2025-02-11 22:44:46', '', '/uploads/5159b173-8912-43dc-86d7-d4319b962d54_APC379.mp4', '/uploads/6bb3ec2d-da95-40c8-aaf2-1e16239cd59b_c3d5e180-9123-4474-92ac-e9ec0e23ebc2.png', '/uploads/bc875cdd-d95c-4881-904c-d9c97a5cb550_Modern-Leather-Led-Chandelier-Dimmable-Dining-Room-Living-Room-Bedroom-Hall-Chandelier-Home-Decoration-Lighting-Fixture-4-1.jpg', '/uploads/98d0adfc-ed2d-46b5-9936-3a832b180d05_Untitled.png', 2, '2131231', '2025-02-12 14:47:07', '2025-02-12 18:02:44');
INSERT INTO `demand_details` VALUES (5, 1, '1100123123', 1100.00, '2025-02-13 09:33:42', '', NULL, NULL, NULL, '/uploads/20250213093353_L-mpara-de-pared-de-cobre-para-decoraci-n-del-hogar-candelabro-de-lujo-creativo-para.jpg', '/uploads/20250213093348_Chinoiserie-Knob-Rattan-Pendant-Light-Creative-Vintage-Design-Lamps-for-Living-Room-Sofa-Kitchen-Table-Decoration-3-1-1-1-1-1.webp', NULL, 1, NULL, '2025-02-13 09:33:55', '2025-02-13 09:33:55');
INSERT INTO `demand_details` VALUES (6, 2, '11000', 1100.00, '2025-02-13 11:14:34', '', NULL, NULL, NULL, '/uploads/20250213111446_FC3EEFA6-14D8-4afb-B862-328CF5694D76.png', '/uploads/20250213111437_4A25F286-7F0E-4589-B214-AA996E97ABF7.png', NULL, 2, NULL, '2025-02-13 11:14:50', '2025-02-13 11:14:50');
INSERT INTO `demand_details` VALUES (7, 2, '123123100010', 11000.00, '2025-02-13 11:17:53', '', NULL, NULL, NULL, '/uploads/20250213111810_c3d5e180-9123-4474-92ac-e9ec0e23ebc2.png', '/uploads/20250213111756_4A25F286-7F0E-4589-B214-AA996E97ABF7.png', NULL, 2, NULL, '2025-02-13 11:18:23', '2025-02-13 11:18:23');

-- ----------------------------
-- Table structure for demand_images
-- ----------------------------
DROP TABLE IF EXISTS `demand_images`;
CREATE TABLE `demand_images`  (
  `image_id` int(11) NOT NULL AUTO_INCREMENT,
  `demand_id` int(11) NOT NULL,
  `image_type` enum('order','review','payment') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `image_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `original_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`image_id`) USING BTREE,
  INDEX `demand_id`(`demand_id`) USING BTREE,
  CONSTRAINT `demand_images_ibfk_1` FOREIGN KEY (`demand_id`) REFERENCES `demands` (`demand_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of demand_images
-- ----------------------------

-- ----------------------------
-- Table structure for demand_mediator_relations
-- ----------------------------
DROP TABLE IF EXISTS `demand_mediator_relations`;
CREATE TABLE `demand_mediator_relations`  (
  `relation_id` int(11) NOT NULL AUTO_INCREMENT,
  `demand_id` int(11) NOT NULL,
  `mediator_id` int(11) NOT NULL,
  `ordered_quantity_by_mediator` int(11) NOT NULL,
  PRIMARY KEY (`relation_id`) USING BTREE,
  INDEX `demand_id`(`demand_id`) USING BTREE,
  INDEX `mediator_id`(`mediator_id`) USING BTREE,
  CONSTRAINT `demand_mediator_relations_ibfk_1` FOREIGN KEY (`demand_id`) REFERENCES `demands` (`demand_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `demand_mediator_relations_ibfk_2` FOREIGN KEY (`mediator_id`) REFERENCES `mediators` (`mediator_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of demand_mediator_relations
-- ----------------------------

-- ----------------------------
-- Table structure for demand_status
-- ----------------------------
DROP TABLE IF EXISTS `demand_status`;
CREATE TABLE `demand_status`  (
  `status_id` int(11) NOT NULL AUTO_INCREMENT,
  `status_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `color` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`status_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of demand_status
-- ----------------------------
INSERT INTO `demand_status` VALUES (1, '进行中', '绿', '需求正在进行中');
INSERT INTO `demand_status` VALUES (2, '暂停', '黄', '需求已暂停');
INSERT INTO `demand_status` VALUES (3, '终止', '灰', '需求已终止');
INSERT INTO `demand_status` VALUES (4, '已完成', '灰', '需求已完成');

-- ----------------------------
-- Table structure for demand_videos
-- ----------------------------
DROP TABLE IF EXISTS `demand_videos`;
CREATE TABLE `demand_videos`  (
  `video_id` int(11) NOT NULL AUTO_INCREMENT,
  `demand_id` int(11) NOT NULL,
  `detail_id` int(11) NULL DEFAULT NULL,
  `video_type` enum('review') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `video_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `original_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`video_id`) USING BTREE,
  INDEX `demand_id`(`demand_id`) USING BTREE,
  INDEX `detail_id`(`detail_id`) USING BTREE,
  CONSTRAINT `demand_videos_ibfk_1` FOREIGN KEY (`demand_id`) REFERENCES `demands` (`demand_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `demand_videos_ibfk_2` FOREIGN KEY (`detail_id`) REFERENCES `demand_details` (`detail_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of demand_videos
-- ----------------------------

-- ----------------------------
-- Table structure for demands
-- ----------------------------
DROP TABLE IF EXISTS `demands`;
CREATE TABLE `demands`  (
  `demand_id` int(11) NOT NULL AUTO_INCREMENT,
  `marketing_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `dingtalk_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `asin` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `assessment_quantity` int(11) NOT NULL,
  `text_review_quantity` int(11) NOT NULL,
  `image_review_quantity` int(11) NOT NULL,
  `video_review_quantity` int(11) NOT NULL,
  `free_review_quantity` int(11) NOT NULL,
  `like_only_quantity` int(11) NOT NULL,
  `fb_order_quantity` int(11) NOT NULL,
  `ordered_quantity` int(11) NOT NULL,
  `unordered_quantity` int(11) NOT NULL,
  `reviewed_quantity` int(11) NOT NULL,
  `unreviewed_quantity` int(11) NOT NULL,
  `registration_date` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `first_order_date` datetime NULL DEFAULT NULL,
  `product_price` decimal(10, 2) NULL DEFAULT NULL,
  `search_keyword` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `hyperlink` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `product_image_url` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `received_product_image_url` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `order_style` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `attribute_value_1` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `attribute_value_2` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `other_notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `status_id` int(11) NOT NULL,
  `model_id` int(11) NOT NULL,
  `type_id` int(11) NOT NULL,
  `platform_id` int(11) NOT NULL,
  `country_id` int(11) NOT NULL,
  `brand_id` int(11) NOT NULL,
  `store_id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `method_id` int(11) NOT NULL,
  `ad_entry_option_id` int(11) NOT NULL,
  `variant_option_id` int(11) NOT NULL,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`demand_id`, `updated_at`) USING BTREE,
  INDEX `status_id`(`status_id`) USING BTREE,
  INDEX `model_id`(`model_id`) USING BTREE,
  INDEX `type_id`(`type_id`) USING BTREE,
  INDEX `platform_id`(`platform_id`) USING BTREE,
  INDEX `country_id`(`country_id`) USING BTREE,
  INDEX `brand_id`(`brand_id`) USING BTREE,
  INDEX `store_id`(`store_id`) USING BTREE,
  INDEX `account_id`(`account_id`) USING BTREE,
  INDEX `method_id`(`method_id`) USING BTREE,
  INDEX `ad_entry_option_id`(`ad_entry_option_id`) USING BTREE,
  INDEX `variant_option_id`(`variant_option_id`) USING BTREE,
  INDEX `demand_id`(`demand_id`) USING BTREE,
  CONSTRAINT `demands_ibfk_1` FOREIGN KEY (`status_id`) REFERENCES `demand_status` (`status_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `demands_ibfk_10` FOREIGN KEY (`ad_entry_option_id`) REFERENCES `ad_entry_options` (`option_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `demands_ibfk_11` FOREIGN KEY (`variant_option_id`) REFERENCES `variant_options` (`option_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `demands_ibfk_2` FOREIGN KEY (`model_id`) REFERENCES `product_models` (`model_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `demands_ibfk_3` FOREIGN KEY (`type_id`) REFERENCES `business_types` (`type_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `demands_ibfk_4` FOREIGN KEY (`platform_id`) REFERENCES `platforms` (`platform_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `demands_ibfk_5` FOREIGN KEY (`country_id`) REFERENCES `countries` (`country_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `demands_ibfk_6` FOREIGN KEY (`brand_id`) REFERENCES `brands` (`brand_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `demands_ibfk_7` FOREIGN KEY (`store_id`) REFERENCES `stores` (`store_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `demands_ibfk_8` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`account_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `demands_ibfk_9` FOREIGN KEY (`method_id`) REFERENCES `search_methods` (`method_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of demands
-- ----------------------------
INSERT INTO `demands` VALUES (1, '1231231231', '23123123', '123123', 123123, 123123, 123123, 123, 123123, 12312, 23123, 123213, 21312, 312312, 3123123, '2024-02-02 22:22:00', '2025-02-02 22:22:00', 222.00, '12312', '12312', '3123', '12312', '3123', '12312', '3123123', '11231', 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, '2025-02-12 13:16:35');
INSERT INTO `demands` VALUES (2, '1341564641', '13156161', '1615561', 111, 11, 111, 11, 0, 0, 0, 0, 0, 0, 0, '2025-02-12 00:00:00', '2025-02-12 00:00:00', NULL, '', 'https://1231.com', '', '', '', '', '', '1231', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, '2025-02-12 15:06:49');
INSERT INTO `demands` VALUES (3, '16160561606', '1561351', '156165165', 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL, NULL, NULL, '', '', NULL, NULL, NULL, NULL, NULL, '', 2, 1, 1, 1, 3, 1, 2, 2, 2, 2, 2, '2025-02-13 11:49:50');

-- ----------------------------
-- Table structure for import_history
-- ----------------------------
DROP TABLE IF EXISTS `import_history`;
CREATE TABLE `import_history`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `filename` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `import_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `success_count` int(11) NULL DEFAULT 0,
  `error_count` int(11) NULL DEFAULT 0,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `error_details` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `imported_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of import_history
-- ----------------------------

-- ----------------------------
-- Table structure for mediators
-- ----------------------------
DROP TABLE IF EXISTS `mediators`;
CREATE TABLE `mediators`  (
  `mediator_id` int(11) NOT NULL AUTO_INCREMENT,
  `mediator_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`mediator_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of mediators
-- ----------------------------

-- ----------------------------
-- Table structure for order_details
-- ----------------------------
DROP TABLE IF EXISTS `order_details`;
CREATE TABLE `order_details`  (
  `order_detail_id` int(11) NOT NULL AUTO_INCREMENT,
  `demand_id` int(11) NOT NULL,
  `ordered_quantity` int(11) NOT NULL,
  `reviewed_quantity` int(11) NOT NULL,
  PRIMARY KEY (`order_detail_id`) USING BTREE,
  INDEX `demand_id`(`demand_id`) USING BTREE,
  CONSTRAINT `order_details_ibfk_1` FOREIGN KEY (`demand_id`) REFERENCES `demands` (`demand_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of order_details
-- ----------------------------

-- ----------------------------
-- Table structure for platforms
-- ----------------------------
DROP TABLE IF EXISTS `platforms`;
CREATE TABLE `platforms`  (
  `platform_id` int(11) NOT NULL AUTO_INCREMENT,
  `platform_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`platform_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of platforms
-- ----------------------------
INSERT INTO `platforms` VALUES (1, '亚马逊');
INSERT INTO `platforms` VALUES (2, 'eBay');
INSERT INTO `platforms` VALUES (3, 'Shopee');
INSERT INTO `platforms` VALUES (4, '亚马逊');
INSERT INTO `platforms` VALUES (5, 'eBay');
INSERT INTO `platforms` VALUES (6, 'Shopee');

-- ----------------------------
-- Table structure for product_models
-- ----------------------------
DROP TABLE IF EXISTS `product_models`;
CREATE TABLE `product_models`  (
  `model_id` int(11) NOT NULL AUTO_INCREMENT,
  `model_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`model_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of product_models
-- ----------------------------
INSERT INTO `product_models` VALUES (1, '型号A');
INSERT INTO `product_models` VALUES (2, '型号B');
INSERT INTO `product_models` VALUES (3, '型号C');
INSERT INTO `product_models` VALUES (4, '型号A');
INSERT INTO `product_models` VALUES (5, '型号B');
INSERT INTO `product_models` VALUES (6, '型号C');

-- ----------------------------
-- Table structure for progress_info
-- ----------------------------
DROP TABLE IF EXISTS `progress_info`;
CREATE TABLE `progress_info`  (
  `progress_id` int(11) NOT NULL AUTO_INCREMENT,
  `demand_id` int(11) NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `progress_percentage` int(11) NOT NULL,
  PRIMARY KEY (`progress_id`) USING BTREE,
  INDEX `demand_id`(`demand_id`) USING BTREE,
  CONSTRAINT `progress_info_ibfk_1` FOREIGN KEY (`demand_id`) REFERENCES `demands` (`demand_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of progress_info
-- ----------------------------

-- ----------------------------
-- Table structure for refund_logs
-- ----------------------------
DROP TABLE IF EXISTS `refund_logs`;
CREATE TABLE `refund_logs`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL COMMENT '关联返款订单ID',
  `action` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '操作类型',
  `old_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '原状态',
  `new_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '新状态',
  `operator` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '操作人',
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '备注',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `order_id`(`order_id`) USING BTREE,
  CONSTRAINT `refund_logs_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `refund_orders` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '返款日志表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of refund_logs
-- ----------------------------
INSERT INTO `refund_logs` VALUES (1, 1, 'payment', 'pending', 'completed', 'system', '创建返款支付记录', '2025-02-12 18:11:25');

-- ----------------------------
-- Table structure for refund_orders
-- ----------------------------
DROP TABLE IF EXISTS `refund_orders`;
CREATE TABLE `refund_orders`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `demand_id` int(11) NULL DEFAULT NULL COMMENT '关联需求ID',
  `detail_id` int(11) NULL DEFAULT NULL COMMENT '关联测评明细ID',
  `marketing_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '营销编号',
  `dingtalk_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '钉钉号',
  `asin` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '商品ASIN',
  `intermediary` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '中介名称',
  `order_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '订单号',
  `order_date` datetime NOT NULL COMMENT '下单日期',
  `order_amount` decimal(10, 2) NOT NULL COMMENT '订单金额',
  `currency` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'USD' COMMENT '币种',
  `review_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '评价类型',
  `business_type` enum('joint','self') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '联营/自营',
  `brand` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '品牌',
  `payment_method` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '支付方式',
  `paypal_principal` decimal(10, 2) NULL DEFAULT NULL COMMENT 'PayPal本金',
  `rmb_commission` decimal(10, 2) NULL DEFAULT NULL COMMENT 'RMB佣金',
  `intermediary_commission` decimal(10, 2) NULL DEFAULT NULL COMMENT '中介佣金',
  `commission_currency` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '佣金币种',
  `exchange_rate` decimal(10, 4) NULL DEFAULT NULL COMMENT '汇率',
  `actual_payment` decimal(10, 2) NULL DEFAULT NULL COMMENT '实际支付金额',
  `status` enum('pending','processing','completed','failed') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'pending' COMMENT '状态',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `demand_id`(`demand_id`) USING BTREE,
  INDEX `detail_id`(`detail_id`) USING BTREE,
  CONSTRAINT `refund_orders_ibfk_1` FOREIGN KEY (`demand_id`) REFERENCES `demands` (`demand_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `refund_orders_ibfk_2` FOREIGN KEY (`detail_id`) REFERENCES `demand_details` (`detail_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '返款订单表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of refund_orders
-- ----------------------------
INSERT INTO `refund_orders` VALUES (1, 2, 4, '1341564641', '13156161', '1615561', NULL, '123123123111', '2025-02-12 18:05:44', 1100.00, 'USD', NULL, 'joint', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'completed', '2025-02-12 18:05:44', '2025-02-12 18:11:25');

-- ----------------------------
-- Table structure for refund_payments
-- ----------------------------
DROP TABLE IF EXISTS `refund_payments`;
CREATE TABLE `refund_payments`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL COMMENT '关联返款订单ID',
  `detail_id` int(11) NULL DEFAULT NULL COMMENT '关联测评明细ID',
  `customer_email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '客户邮箱',
  `order_amount` decimal(10, 2) NOT NULL COMMENT '订单金额',
  `transfer_amount` decimal(10, 2) NOT NULL COMMENT '转账金额',
  `currency` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '币种',
  `intermediary_commission` decimal(10, 2) NULL DEFAULT NULL COMMENT '中介佣金',
  `commission_currency` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '佣金币种',
  `rmb_commission` decimal(10, 2) NULL DEFAULT NULL COMMENT 'RMB佣金',
  `payment_method` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '支付方式',
  `payment_account` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '支付账号',
  `payment_time` datetime NOT NULL COMMENT '支付时间',
  `payment_screenshot` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '支付截图',
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '备注',
  `status` enum('pending','completed','failed') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'pending' COMMENT '状态',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `order_id`(`order_id`) USING BTREE,
  INDEX `detail_id`(`detail_id`) USING BTREE,
  CONSTRAINT `refund_payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `refund_orders` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `refund_payments_ibfk_2` FOREIGN KEY (`detail_id`) REFERENCES `demand_details` (`detail_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '返款支付表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of refund_payments
-- ----------------------------
INSERT INTO `refund_payments` VALUES (1, 1, 4, '15615@063.com', 1100.00, 1100.00, 'USD', 0.00, NULL, 0.00, 'PayPal', '1316', '2025-02-12 18:10:41', '/uploads/74e1e9b7-bf24-4bf3-a142-e13d825b4078_FC3EEFA6-14D8-4afb-B862-328CF5694D76.png', '', 'pending', '2025-02-12 18:11:25', '2025-02-12 18:11:25');

-- ----------------------------
-- Table structure for refund_reviews
-- ----------------------------
DROP TABLE IF EXISTS `refund_reviews`;
CREATE TABLE `refund_reviews`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL COMMENT '关联返款订单ID',
  `detail_id` int(11) NULL DEFAULT NULL COMMENT '关联测评明细ID',
  `review_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '评价类型',
  `review_link` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '评价链接',
  `screenshot1` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '评价截图1',
  `screenshot2` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '评价截图2',
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '备注',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `order_id`(`order_id`) USING BTREE,
  INDEX `detail_id`(`detail_id`) USING BTREE,
  CONSTRAINT `refund_reviews_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `refund_orders` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `refund_reviews_ibfk_2` FOREIGN KEY (`detail_id`) REFERENCES `demand_details` (`detail_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '返款评价表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of refund_reviews
-- ----------------------------

-- ----------------------------
-- Table structure for search_methods
-- ----------------------------
DROP TABLE IF EXISTS `search_methods`;
CREATE TABLE `search_methods`  (
  `method_id` int(11) NOT NULL AUTO_INCREMENT,
  `method_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`method_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of search_methods
-- ----------------------------
INSERT INTO `search_methods` VALUES (1, '前台搜索');
INSERT INTO `search_methods` VALUES (2, '类目搜索');

-- ----------------------------
-- Table structure for stores
-- ----------------------------
DROP TABLE IF EXISTS `stores`;
CREATE TABLE `stores`  (
  `store_id` int(11) NOT NULL AUTO_INCREMENT,
  `store_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`store_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of stores
-- ----------------------------
INSERT INTO `stores` VALUES (1, '店铺A');
INSERT INTO `stores` VALUES (2, '店铺B');
INSERT INTO `stores` VALUES (3, '店铺C');
INSERT INTO `stores` VALUES (4, '店铺A');
INSERT INTO `stores` VALUES (5, '店铺B');
INSERT INTO `stores` VALUES (6, '店铺C');

-- ----------------------------
-- Table structure for system_info_table
-- ----------------------------
DROP TABLE IF EXISTS `system_info_table`;
CREATE TABLE `system_info_table`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_model` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `business_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `platform` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `country` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `brand` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `store` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `account` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of system_info_table
-- ----------------------------

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'user',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'vben', '123456', 'user');

-- ----------------------------
-- Table structure for variant_options
-- ----------------------------
DROP TABLE IF EXISTS `variant_options`;
CREATE TABLE `variant_options`  (
  `option_id` int(11) NOT NULL AUTO_INCREMENT,
  `option_name` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`option_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of variant_options
-- ----------------------------
INSERT INTO `variant_options` VALUES (1, '是');
INSERT INTO `variant_options` VALUES (2, '否');

SET FOREIGN_KEY_CHECKS = 1;
