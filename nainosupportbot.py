<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Darbar Admin Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-firestore-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-auth-compat.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        body { 
            font-family: 'Poppins', sans-serif; 
            background: linear-gradient(135deg, #f5f7fa 0%, #e4efe9 100%);
        }
        
        .brand-color { 
            background: linear-gradient(135deg, #800000 0%, #5c0000 100%);
            box-shadow: 0 4px 15px rgba(128, 0, 0, 0.2);
        } 
        
        .text-brand { 
            color: #800000; 
        }
        
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        }
        
        .stat-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            padding: 20px;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(135deg, #800000 0%, #5c0000 100%);
        }
        
        .stat-icon {
            width: 50px;
            height: 50px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #800000 0%, #5c0000 100%);
            transition: all 0.3s ease;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(128, 0, 0, 0.3);
        }
        
        .btn-secondary {
            border: 1px solid #800000;
            color: #800000;
            transition: all 0.3s ease;
        }
        
        .btn-secondary:hover {
            background-color: rgba(128, 0, 0, 0.05);
        }
        
        .sidebar-item {
            transition: all 0.3s ease;
            border-radius: 8px;
            margin-bottom: 5px;
        }
        
        .sidebar-item:hover {
            background-color: rgba(128, 0, 0, 0.05);
        }
        
        .sidebar-item.active {
            background: linear-gradient(135deg, rgba(128, 0, 0, 0.1) 0%, rgba(92, 0, 0, 0.1) 100%);
            border-left: 3px solid #800000;
        }
        
        .order-card {
            transition: all 0.3s ease;
        }
        
        .order-card:hover {
            transform: translateX(5px);
        }
        
        .food-item-card {
            transition: all 0.3s ease;
        }
        
        .food-item-card:hover {
            transform: scale(1.02);
        }
        
        .banner-item {
            transition: all 0.3s ease;
        }
        
        .banner-item:hover {
            transform: scale(1.02);
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification.success {
            border-left: 4px solid #4caf50;
        }
        
        .notification.error {
            border-left: 4px solid #f44336;
        }
        
        .notification i {
            font-size: 20px;
        }
        
        .notification.success i {
            color: #4caf50;
        }
        
        .notification.error i {
            color: #f44336;
        }
        
        .loading-spinner {
            border: 3px solid rgba(128, 0, 0, 0.1);
            border-radius: 50%;
            border-top: 3px solid #800000;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .tab-button {
            position: relative;
            transition: all 0.3s ease;
        }
        
        .tab-button.active::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(135deg, #800000 0%, #5c0000 100%);
        }
        
        .status-badge {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-pending {
            background-color: rgba(255, 193, 7, 0.2);
            color: #856404;
        }
        
        .status-accepted {
            background-color: rgba(76, 175, 80, 0.2);
            color: #2e7d32;
        }
        
        .status-completed {
            background-color: rgba(33, 150, 243, 0.2);
            color: #0d47a1;
        }
        
        .status-cancelled {
            background-color: rgba(244, 67, 54, 0.2);
            color: #b71c1c;
        }
    </style>
</head>
<body class="bg-gray-100">

    <!-- Notification Container -->
    <div id="notification" class="notification">
        <i class="fas fa-check-circle"></i>
        <span id="notificationText">Operation successful!</span>
    </div>

    <!-- Login Screen -->
    <div id="loginScreen" class="h-screen flex items-center justify-center">
        <div class="card p-8 w-96" data-aos="fade-up">
            <div class="text-center mb-6">
                <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-red-600 to-red-800 rounded-full mb-4">
                    <i class="fas fa-cookie-bite text-white text-3xl"></i>
                </div>
                <h1 class="text-2xl font-bold text-gray-800">Darbar Admin Panel</h1>
                <p class="text-gray-500 text-sm mt-2">Sign in to manage your business</p>
            </div>
            <div class="space-y-4">
                <div class="relative">
                    <input type="email" id="email" placeholder="Email" class="w-full p-3 pl-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                    <i class="fas fa-envelope absolute left-3 top-3.5 text-gray-400"></i>
                </div>
                <div class="relative">
                    <input type="password" id="password" placeholder="Password" class="w-full p-3 pl-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                    <i class="fas fa-lock absolute left-3 top-3.5 text-gray-400"></i>
                </div>
                <button onclick="login()" class="w-full btn-primary text-white py-3 rounded-lg font-medium">
                    <i class="fas fa-sign-in-alt mr-2"></i> Sign In
                </button>
            </div>
        </div>
    </div>

    <!-- Dashboard -->
    <div id="dashboard" class="hidden min-h-screen">
        <!-- Header -->
        <header class="brand-color text-white p-4 shadow-md">
            <div class="flex justify-between items-center">
                <div class="flex items-center gap-3">
                    <i class="fas fa-cookie-bite text-2xl"></i>
                    <h1 class="text-xl font-bold">Darbar Owner Panel</h1>
                </div>
                <div class="flex items-center gap-4">
                    <div class="relative">
                        <button class="p-2 rounded-full hover:bg-red-700 transition">
                            <i class="fas fa-bell"></i>
                            <span class="absolute top-0 right-0 w-2 h-2 bg-yellow-400 rounded-full"></span>
                        </button>
                    </div>
                    <div class="flex items-center gap-2">
                        <img src="https://picsum.photos/seed/admin/40/40.jpg" class="w-8 h-8 rounded-full">
                        <span class="text-sm">Admin</span>
                    </div>
                    <button onclick="logout()" class="text-sm bg-red-700 hover:bg-red-800 px-3 py-1 rounded transition">
                        <i class="fas fa-sign-out-alt mr-1"></i> Logout
                    </button>
                </div>
            </div>
        </header>

        <div class="flex">
            <!-- Sidebar -->
            <aside class="w-64 bg-white h-screen shadow-md p-4">
                <nav>
                    <button onclick="showSection('overviewSec')" class="sidebar-item active w-full text-left p-3 flex items-center gap-3">
                        <i class="fas fa-tachometer-alt text-brand"></i>
                        <span>Overview</span>
                    </button>
                    <button onclick="showSection('ordersSec')" class="sidebar-item w-full text-left p-3 flex items-center gap-3">
                        <i class="fas fa-shopping-cart text-brand"></i>
                        <span>Orders</span>
                    </button>
                    <button onclick="showSection('foodSec')" class="sidebar-item w-full text-left p-3 flex items-center gap-3">
                        <i class="fas fa-utensils text-brand"></i>
                        <span>Manage Food</span>
                    </button>
                    <button onclick="showSection('bannerSec')" class="sidebar-item w-full text-left p-3 flex items-center gap-3">
                        <i class="fas fa-images text-brand"></i>
                        <span>Manage Banners</span>
                    </button>
                    <button onclick="showSection('analyticsSec')" class="sidebar-item w-full text-left p-3 flex items-center gap-3">
                        <i class="fas fa-chart-line text-brand"></i>
                        <span>Analytics</span>
                    </button>
                    <button onclick="showSection('settingsSec')" class="sidebar-item w-full text-left p-3 flex items-center gap-3">
                        <i class="fas fa-cog text-brand"></i>
                        <span>Settings</span>
                    </button>
                </nav>
            </aside>

            <!-- Main Content -->
            <main class="flex-1 p-6">
                <!-- 1. Overview Section -->
                <div id="overviewSec" class="section-content">
                    <h2 class="text-2xl font-bold mb-6 text-gray-800">Dashboard Overview</h2>
                    
                    <!-- Stats Cards -->
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <div class="stat-card" data-aos="fade-up" data-aos-delay="100">
                            <div class="flex justify-between items-center">
                                <div>
                                    <p class="text-gray-500 text-sm">Total Orders</p>
                                    <p class="text-2xl font-bold text-gray-800" id="totalOrdersCount">0</p>
                                    <p class="text-xs text-green-500 mt-1">
                                        <i class="fas fa-arrow-up"></i> 12% from last month
                                    </p>
                                </div>
                                <div class="stat-icon bg-blue-100 text-blue-600">
                                    <i class="fas fa-shopping-bag"></i>
                                </div>
                            </div>
                        </div>
                        
                        <div class="stat-card" data-aos="fade-up" data-aos-delay="200">
                            <div class="flex justify-between items-center">
                                <div>
                                    <p class="text-gray-500 text-sm">Total Revenue</p>
                                    <p class="text-2xl font-bold text-gray-800" id="totalRevenue">₹0</p>
                                    <p class="text-xs text-green-500 mt-1">
                                        <i class="fas fa-arrow-up"></i> 8% from last month
                                    </p>
                                </div>
                                <div class="stat-icon bg-green-100 text-green-600">
                                    <i class="fas fa-rupee-sign"></i>
                                </div>
                            </div>
                        </div>
                        
                        <div class="stat-card" data-aos="fade-up" data-aos-delay="300">
                            <div class="flex justify-between items-center">
                                <div>
                                    <p class="text-gray-500 text-sm">Total Customers</p>
                                    <p class="text-2xl font-bold text-gray-800" id="totalCustomers">0</p>
                                    <p class="text-xs text-green-500 mt-1">
                                        <i class="fas fa-arrow-up"></i> 5% from last month
                                    </p>
                                </div>
                                <div class="stat-icon bg-purple-100 text-purple-600">
                                    <i class="fas fa-users"></i>
                                </div>
                            </div>
                        </div>
                        
                        <div class="stat-card" data-aos="fade-up" data-aos-delay="400">
                            <div class="flex justify-between items-center">
                                <div>
                                    <p class="text-gray-500 text-sm">Menu Items</p>
                                    <p class="text-2xl font-bold text-gray-800" id="totalMenuItems">0</p>
                                    <p class="text-xs text-gray-500 mt-1">
                                        <i class="fas fa-minus"></i> No change
                                    </p>
                                </div>
                                <div class="stat-icon bg-red-100 text-red-600">
                                    <i class="fas fa-utensils"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Recent Orders and Chart -->
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div class="card p-6" data-aos="fade-up" data-aos-delay="500">
                            <h3 class="text-lg font-semibold mb-4 text-gray-800">Recent Orders</h3>
                            <div id="recentOrdersList" class="space-y-3">
                                <!-- Recent orders loaded here -->
                            </div>
                        </div>
                        
                        <div class="card p-6" data-aos="fade-up" data-aos-delay="600">
                            <h3 class="text-lg font-semibold mb-4 text-gray-800">Sales Overview</h3>
                            <canvas id="salesChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                </div>

                <!-- 2. Orders Section -->
                <div id="ordersSec" class="section-content hidden">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-2xl font-bold text-gray-800">Orders Management</h2>
                        <div class="flex gap-2">
                            <button class="btn-secondary px-4 py-2 rounded-lg text-sm">
                                <i class="fas fa-filter mr-2"></i> Filter
                            </button>
                            <button class="btn-secondary px-4 py-2 rounded-lg text-sm">
                                <i class="fas fa-download mr-2"></i> Export
                            </button>
                        </div>
                    </div>
                    
                    <!-- Order Status Tabs -->
                    <div class="flex gap-2 mb-6 border-b">
                        <button onclick="filterOrders('all')" class="tab-button active px-4 py-2 text-sm font-medium">All Orders</button>
                        <button onclick="filterOrders('pending')" class="tab-button px-4 py-2 text-sm font-medium">Pending</button>
                        <button onclick="filterOrders('accepted')" class="tab-button px-4 py-2 text-sm font-medium">Accepted</button>
                        <button onclick="filterOrders('completed')" class="tab-button px-4 py-2 text-sm font-medium">Completed</button>
                        <button onclick="filterOrders('cancelled')" class="tab-button px-4 py-2 text-sm font-medium">Cancelled</button>
                    </div>
                    
                    <div id="ordersList" class="space-y-4">
                        <!-- Orders Loaded Here -->
                    </div>
                </div>

                <!-- 3. Food Management -->
                <div id="foodSec" class="section-content hidden">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-2xl font-bold text-gray-800">Food Management</h2>
                        <button onclick="toggleAddFoodForm()" class="btn-primary text-white px-4 py-2 rounded-lg">
                            <i class="fas fa-plus mr-2"></i> Add New Item
                        </button>
                    </div>
                    
                    <!-- Add Food Form -->
                    <div id="addFoodForm" class="card p-6 mb-6 hidden" data-aos="fade-up">
                        <h3 class="text-lg font-semibold mb-4 text-gray-800">Add New Food Item</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Food Name</label>
                                <input type="text" id="fName" placeholder="Enter food name" class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Price</label>
                                <input type="number" id="fPrice" placeholder="Enter price" class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Image URL</label>
                                <input type="url" id="fImg" placeholder="https://..." class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
                                <select id="fCategory" class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                                    <option value="sweets">Sweets</option>
                                    <option value="savory">Savory</option>
                                    <option value="beverages">Beverages</option>
                                    <option value="special">Special</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
                                <select id="fType" class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                                    <option value="veg">Veg</option>
                                    <option value="nonveg">Non-Veg</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                                <input type="text" id="fDescription" placeholder="Brief description" class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                            </div>
                            <div class="md:col-span-2">
                                <label class="flex items-center">
                                    <input type="checkbox" id="fSpecial" class="mr-2">
                                    <span class="text-sm font-medium text-gray-700">Mark as Special Item</span>
                                </label>
                            </div>
                            <div class="md:col-span-2">
                                <button onclick="addFood()" class="btn-primary text-white px-4 py-2 rounded-lg">
                                    <i class="fas fa-save mr-2"></i> Save Item
                                </button>
                                <button onclick="toggleAddFoodForm()" class="btn-secondary px-4 py-2 rounded-lg ml-2">
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div id="foodList" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <!-- Food Items Loaded Here -->
                    </div>
                </div>

                <!-- 4. Banner Management -->
                <div id="bannerSec" class="section-content hidden">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-2xl font-bold text-gray-800">Banner Management</h2>
                        <button onclick="toggleAddBannerForm()" class="btn-primary text-white px-4 py-2 rounded-lg">
                            <i class="fas fa-plus mr-2"></i> Add New Banner
                        </button>
                    </div>
                    
                    <!-- Add Banner Form -->
                    <div id="addBannerForm" class="card p-6 mb-6 hidden" data-aos="fade-up">
                        <h3 class="text-lg font-semibold mb-4 text-gray-800">Add New Banner</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Banner Image URL</label>
                                <input type="url" id="bImg" placeholder="https://..." class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Display Order</label>
                                <input type="number" id="bOrder" placeholder="1, 2, 3..." class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                            </div>
                            <div class="md:col-span-2">
                                <label class="flex items-center">
                                    <input type="checkbox" id="bActive" checked class="mr-2">
                                    <span class="text-sm font-medium text-gray-700">Make this banner active</span>
                                </label>
                            </div>
                            <div class="md:col-span-2">
                                <button onclick="addBanner()" class="btn-primary text-white px-4 py-2 rounded-lg">
                                    <i class="fas fa-save mr-2"></i> Save Banner
                                </button>
                                <button onclick="toggleAddBannerForm()" class="btn-secondary px-4 py-2 rounded-lg ml-2">
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div id="bannerList" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <!-- Banners Loaded Here -->
                    </div>
                </div>
                
                <!-- 5. Analytics Section -->
                <div id="analyticsSec" class="section-content hidden">
                    <h2 class="text-2xl font-bold mb-6 text-gray-800">Analytics</h2>
                    
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                        <div class="card p-6">
                            <h3 class="text-lg font-semibold mb-4 text-gray-800">Sales by Category</h3>
                            <canvas id="categoryChart" width="400" height="200"></canvas>
                        </div>
                        
                        <div class="card p-6">
                            <h3 class="text-lg font-semibold mb-4 text-gray-800">Order Status Distribution</h3>
                            <canvas id="statusChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                    
                    <div class="card p-6">
                        <h3 class="text-lg font-semibold mb-4 text-gray-800">Top Selling Items</h3>
                        <div id="topSellingItems" class="space-y-3">
                            <!-- Top selling items loaded here -->
                        </div>
                    </div>
                </div>
                
                <!-- 6. Settings Section -->
                <div id="settingsSec" class="section-content hidden">
                    <h2 class="text-2xl font-bold mb-6 text-gray-800">Settings</h2>
                    
                    <div class="card p-6">
                        <h3 class="text-lg font-semibold mb-4 text-gray-800">Store Information</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Store Name</label>
                                <input type="text" value="Darbar Sweet" class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                                <input type="tel" value="+91 98765 43210" class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                            </div>
                            <div class="md:col-span-2">
                                <label class="block text-sm font-medium text-gray-700 mb-1">Address</label>
                                <textarea class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500" rows="3">123 Main Street, City, State - 123456</textarea>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                <input type="email" value="info@darbarsweet.com" class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Website</label>
                                <input type="url" value="https://darbarsweet.com" class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                            </div>
                            <div class="md:col-span-2">
                                <button class="btn-primary text-white px-4 py-2 rounded-lg">
                                    <i class="fas fa-save mr-2"></i> Save Changes
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script src="config.js"></script>
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script>
        // Initialize AOS
        AOS.init({
            duration: 800,
            once: true
        });
        
        // Auth Logic
        function login() {
            const e = document.getElementById('email').value;
            const p = document.getElementById('password').value;
            
            if (!e || !p) {
                showNotification('Please enter email and password', 'error');
                return;
            }
            
            auth.signInWithEmailAndPassword(e, p).then(() => {
                document.getElementById('loginScreen').classList.add('hidden');
                document.getElementById('dashboard').classList.remove('hidden');
                loadData();
                showNotification('Login successful!', 'success');
            }).catch(err => {
                showNotification(err.message, 'error');
            });
        }

        function logout() { 
            auth.signOut().then(() => {
                location.reload();
                showNotification('Logged out successfully', 'success');
            });
        }

        function showSection(id) {
            // Update sidebar active state
            document.querySelectorAll('.sidebar-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.closest('.sidebar-item').classList.add('active');
            
            // Show selected section
            document.querySelectorAll('.section-content').forEach(section => {
                section.classList.add('hidden');
            });
            document.getElementById(id).classList.remove('hidden');
            
            // Initialize charts if analytics section
            if (id === 'analyticsSec') {
                setTimeout(initCharts, 100);
            }
        }
        
        // Toggle Add Food Form
        function toggleAddFoodForm() {
            const form = document.getElementById('addFoodForm');
            form.classList.toggle('hidden');
        }
        
        // Toggle Add Banner Form
        function toggleAddBannerForm() {
            const form = document.getElementById('addBannerForm');
            form.classList.toggle('hidden');
        }
        
        // Filter Orders by Status
        function filterOrders(status) {
            // Update tab active state
            document.querySelectorAll('.tab-button').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Filter orders
            const orders = document.querySelectorAll('.order-card');
            orders.forEach(order => {
                if (status === 'all' || order.dataset.status === status) {
                    order.style.display = 'block';
                } else {
                    order.style.display = 'none';
                }
            });
        }
        
        // Notification System
        function showNotification(message, type) {
            const notification = document.getElementById('notification');
            const notificationText = document.getElementById('notificationText');
            const icon = notification.querySelector('i');
            
            notificationText.textContent = message;
            notification.className = `notification ${type}`;
            
            if (type === 'success') {
                icon.className = 'fas fa-check-circle';
            } else if (type === 'error') {
                icon.className = 'fas fa-exclamation-circle';
            }
            
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }
        
        // Initialize Charts
        function initCharts() {
            // Sales Chart
            const salesCtx = document.getElementById('salesChart').getContext('2d');
            new Chart(salesCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Sales',
                        data: [12000, 19000, 15000, 25000, 22000, 30000],
                        backgroundColor: 'rgba(128, 0, 0, 0.2)',
                        borderColor: 'rgba(128, 0, 0, 1)',
                        borderWidth: 2,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '₹' + value;
                                }
                            }
                        }
                    }
                }
            });
            
            // Category Chart
            const categoryCtx = document.getElementById('categoryChart').getContext('2d');
            new Chart(categoryCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Sweets', 'Savory', 'Beverages', 'Special'],
                    datasets: [{
                        data: [45, 25, 15, 15],
                        backgroundColor: [
                            'rgba(128, 0, 0, 0.8)',
                            'rgba(255, 193, 7, 0.8)',
                            'rgba(76, 175, 80, 0.8)',
                            'rgba(33, 150, 243, 0.8)'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
            
            // Status Chart
            const statusCtx = document.getElementById('statusChart').getContext('2d');
            new Chart(statusCtx, {
                type: 'pie',
                data: {
                    labels: ['Pending', 'Accepted', 'Completed', 'Cancelled'],
                    datasets: [{
                        data: [15, 30, 50, 5],
                        backgroundColor: [
                            'rgba(255, 193, 7, 0.8)',
                            'rgba(76, 175, 80, 0.8)',
                            'rgba(33, 150, 243, 0.8)',
                            'rgba(244, 67, 54, 0.8)'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }

        // Data Logic
        function loadData() {
            // Load Orders
            db.collection('orders').orderBy('createdAt', 'desc').limit(20).onSnapshot(snap => {
                const div = document.getElementById('ordersList');
                const recentDiv = document.getElementById('recentOrdersList');
                div.innerHTML = '';
                recentDiv.innerHTML = '';
                
                let totalOrders = 0;
                let totalRevenue = 0;
                const customers = new Set();
                const statusCounts = {
                    pending: 0,
                    accepted: 0,
                    completed: 0,
                    cancelled: 0
                };
                
                snap.forEach((doc, index) => {
                    const d = doc.data();
                    totalOrders++;
                    totalRevenue += parseInt(d.totalAmount);
                    customers.add(d.customer.phone);
                    statusCounts[d.status]++;
                    
                    const statusClass = `status-${d.status}`;
                    const statusText = d.status.charAt(0).toUpperCase() + d.status.slice(1);
                    
                    // Main orders list
                    div.innerHTML += `
                        <div class="order-card card p-4" data-status="${d.status}" data-aos="fade-up" data-aos-delay="${index * 50}">
                            <div class="flex justify-between items-start">
                                <div>
                                    <h3 class="font-bold text-gray-800">${d.customer.name}</h3>
                                    <p class="text-sm text-gray-600 mt-1">${d.customer.phone}</p>
                                    <p class="text-xs text-gray-500 mt-1">${d.customer.address}</p>
                                </div>
                                <span class="status-badge ${statusClass}">${statusText}</span>
                            </div>
                            <div class="mt-3">
                                <p class="text-sm text-gray-600">${d.itemsText}</p>
                                <p class="font-bold mt-2 text-brand">Total: ₹${d.totalAmount}</p>
                            </div>
                            <div class="mt-3 flex gap-2">
                                ${d.status === 'pending' ? `
                                    <button onclick="updateOrderStatus('${doc.id}', 'accepted')" class="btn-primary text-white text-xs px-3 py-1 rounded">
                                        <i class="fas fa-check mr-1"></i> Accept
                                    </button>
                                    <button onclick="updateOrderStatus('${doc.id}', 'cancelled')" class="btn-secondary text-xs px-3 py-1 rounded">
                                        <i class="fas fa-times mr-1"></i> Cancel
                                    </button>
                                ` : ''}
                                ${d.status === 'accepted' ? `
                                    <button onclick="updateOrderStatus('${doc.id}', 'completed')" class="btn-primary text-white text-xs px-3 py-1 rounded">
                                        <i class="fas fa-check mr-1"></i> Mark Complete
                                    </button>
                                ` : ''}
                            </div>
                        </div>
                    `;
                    
                    // Recent orders list (only first 5)
                    if (index < 5) {
                        recentDiv.innerHTML += `
                            <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                                <div>
                                    <p class="font-medium text-gray-800">${d.customer.name}</p>
                                    <p class="text-xs text-gray-500">${d.itemsText}</p>
                                </div>
                                <div class="text-right">
                                    <p class="font-bold text-brand">₹${d.totalAmount}</p>
                                    <span class="status-badge ${statusClass}">${statusText}</span>
                                </div>
                            </div>
                        `;
                    }
                });
                
                // Update overview stats
                document.getElementById('totalOrdersCount').textContent = totalOrders;
                document.getElementById('totalRevenue').textContent = `₹${totalRevenue}`;
                document.getElementById('totalCustomers').textContent = customers.size;
                
                // Update top selling items
                updateTopSellingItems();
            });

            // Load Food
            db.collection('menu').onSnapshot(snap => {
                const div = document.getElementById('foodList');
                div.innerHTML = '';
                
                let menuItemsCount = 0;
                
                snap.forEach(doc => {
                    const d = doc.data();
                    menuItemsCount++;
                    
                    div.innerHTML += `
                        <div class="food-item-card card overflow-hidden" data-aos="fade-up">
                            <img src="${d.imageUrl}" class="w-full h-40 object-cover">
                            <div class="p-4">
                                <div class="flex justify-between items-start mb-2">
                                    <h3 class="font-bold text-gray-800">${d.name}</h3>
                                    <span class="text-brand font-bold">₹${d.price}</span>
                                </div>
                                <div class="flex items-center gap-2 mb-2">
                                    <div class="veg-icon"><div class="${d.type === 'veg' ? 'veg-dot' : 'bg-red-600 w-2 h-2 rounded-full'}"></div></div>
                                    <span class="text-xs text-gray-500">${d.category}</span>
                                    ${d.isSpecial ? '<span class="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded">Special</span>' : ''}
                                </div>
                                <p class="text-sm text-gray-600 mb-3">${d.description || 'No description available'}</p>
                                <div class="flex justify-between items-center">
                                    <span class="text-xs ${d.available ? 'text-green-600' : 'text-red-600'}">
                                        ${d.available ? 'Available' : 'Unavailable'}
                                    </span>
                                    <div class="flex gap-2">
                                        <button onclick="toggleFoodAvailability('${doc.id}', ${!d.available})" class="text-xs ${d.available ? 'text-red-500' : 'text-green-500'}">
                                            <i class="fas ${d.available ? 'fa-eye-slash' : 'fa-eye'}"></i>
                                        </button>
                                        <button onclick="editFoodItem('${doc.id}')" class="text-xs text-blue-500">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button onclick="deleteFoodItem('${doc.id}')" class="text-xs text-red-500">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>`;
                });
                
                // Update overview stats
                document.getElementById('totalMenuItems').textContent = menuItemsCount;
            });

            // Load Banners
            db.collection('banners').onSnapshot(snap => {
                const div = document.getElementById('bannerList');
                div.innerHTML = '';
                snap.forEach(doc => {
                    const d = doc.data();
                    div.innerHTML += `
                        <div class="banner-item card overflow-hidden" data-aos="fade-up">
                            <img src="${d.imageUrl}" class="w-full h-40 object-cover">
                            <div class="p-4">
                                <div class="flex justify-between items-center mb-2">
                                    <span class="text-xs ${d.active ? 'text-green-600' : 'text-red-600'}">
                                        ${d.active ? 'Active' : 'Inactive'}
                                    </span>
                                    <span class="text-xs text-gray-500">Order: ${d.order}</span>
                                </div>
                                <div class="flex justify-end gap-2">
                                    <button onclick="toggleBannerStatus('${doc.id}', ${!d.active})" class="text-xs ${d.active ? 'text-red-500' : 'text-green-500'}">
                                        <i class="fas ${d.active ? 'fa-eye-slash' : 'fa-eye'}"></i>
                                    </button>
                                    <button onclick="deleteBannerItem('${doc.id}')" class="text-xs text-red-500">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>`;
                });
            });
        }
        
        // Update Top Selling Items
        function updateTopSellingItems() {
            const topItemsDiv = document.getElementById('topSellingItems');
            topItemsDiv.innerHTML = '';
            
            // Get all orders and calculate item counts
            db.collection('orders').get().then(snap => {
                const itemCounts = {};
                
                snap.forEach(doc => {
                    const order = doc.data();
                    order.items.forEach(item => {
                        if (itemCounts[item.name]) {
                            itemCounts[item.name].count += 1;
                            itemCounts[item.name].revenue += parseInt(item.price);
                        } else {
                            itemCounts[item.name] = {
                                count: 1,
                                revenue: parseInt(item.price),
                                image: item.imageUrl
                            };
                        }
                    });
                });
                
                // Sort by count and get top 5
                const sortedItems = Object.entries(itemCounts)
                    .sort((a, b) => b[1].count - a[1].count)
                    .slice(0, 5);
                
                // Render top items
                sortedItems.forEach((item, index) => {
                    const [name, data] = item;
                    topItemsDiv.innerHTML += `
                        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div class="flex items-center gap-3">
                                <span class="text-lg font-bold text-gray-400">${index + 1}</span>
                                <img src="${data.image}" class="w-10 h-10 rounded object-cover">
                                <div>
                                    <p class="font-medium text-gray-800">${name}</p>
                                    <p class="text-xs text-gray-500">${data.count} orders</p>
                                </div>
                            </div>
                            <div class="text-right">
                                <p class="font-bold text-brand">₹${data.revenue}</p>
                            </div>
                        </div>
                    `;
                });
            });
        }
        
        // Update Order Status
        function updateOrderStatus(orderId, newStatus) {
            db.collection('orders').doc(orderId).update({
                status: newStatus
            }).then(() => {
                showNotification(`Order status updated to ${newStatus}`, 'success');
            }).catch(error => {
                showNotification('Error updating order status', 'error');
                console.error("Error:", error);
            });
        }
        
        // Toggle Food Availability
        function toggleFoodAvailability(itemId, newStatus) {
            db.collection('menu').doc(itemId).update({
                available: newStatus
            }).then(() => {
                showNotification(`Item ${newStatus ? 'available' : 'unavailable'}`, 'success');
            }).catch(error => {
                showNotification('Error updating item availability', 'error');
                console.error("Error:", error);
            });
        }
        
        // Toggle Banner Status
        function toggleBannerStatus(bannerId, newStatus) {
            db.collection('banners').doc(bannerId).update({
                active: newStatus
            }).then(() => {
                showNotification(`Banner ${newStatus ? 'active' : 'inactive'}`, 'success');
            }).catch(error => {
                showNotification('Error updating banner status', 'error');
                console.error("Error:", error);
            });
        }
        
        // Delete Food Item
        function deleteFoodItem(itemId) {
            if (confirm('Are you sure you want to delete this item?')) {
                db.collection('menu').doc(itemId).delete().then(() => {
                    showNotification('Item deleted successfully', 'success');
                }).catch(error => {
                    showNotification('Error deleting item', 'error');
                    console.error("Error:", error);
                });
            }
        }
        
        // Delete Banner Item
        function deleteBannerItem(bannerId) {
            if (confirm('Are you sure you want to delete this banner?')) {
                db.collection('banners').doc(bannerId).delete().then(() => {
                    showNotification('Banner deleted successfully', 'success');
                }).catch(error => {
                    showNotification('Error deleting banner', 'error');
                    console.error("Error:", error);
                });
            }
        }
        
        // Edit Food Item (simplified for demo)
        function editFoodItem(itemId) {
            showNotification('Edit functionality would open a form with current item data', 'success');
        }

        // Add Functions
        function addFood() {
            const name = document.getElementById('fName').value;
            const price = document.getElementById('fPrice').value;
            const imageUrl = document.getElementById('fImg').value;
            const category = document.getElementById('fCategory').value;
            const type = document.getElementById('fType').value;
            const description = document.getElementById('fDescription').value;
            const isSpecial = document.getElementById('fSpecial').checked;
            
            if (!name || !price || !imageUrl) {
                showNotification('Please fill all required fields', 'error');
                return;
            }
            
            db.collection('menu').add({
                name,
                price,
                imageUrl,
                category,
                type,
                description,
                isSpecial,
                available: true
            }).then(() => {
                showNotification('Food item added successfully', 'success');
                toggleAddFoodForm();
                
                // Reset form
                document.getElementById('fName').value = '';
                document.getElementById('fPrice').value = '';
                document.getElementById('fImg').value = '';
                document.getElementById('fDescription').value = '';
                document.getElementById('fSpecial').checked = false;
            }).catch(error => {
                showNotification('Error adding food item', 'error');
                console.error("Error:", error);
            });
        }

        function addBanner() {
            const imageUrl = document.getElementById('bImg').value;
            const order = document.getElementById('bOrder').value || 1;
            const active = document.getElementById('bActive').checked;
            
            if (!imageUrl) {
                showNotification('Please provide banner image URL', 'error');
                return;
            }
            
            db.collection('banners').add({
                imageUrl,
                order: parseInt(order),
                active
            }).then(() => {
                showNotification('Banner added successfully', 'success');
                toggleAddBannerForm();
                
                // Reset form
                document.getElementById('bImg').value = '';
                document.getElementById('bOrder').value = '';
                document.getElementById('bActive').checked = true;
            }).catch(error => {
                showNotification('Error adding banner', 'error');
                console.error("Error:", error);
            });
        }
    </script>
</body>
</html>
