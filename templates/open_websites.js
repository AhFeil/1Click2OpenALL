<script type="text/javascript">
    function openWebsites() {
        var websites = {{ websites|tojson }};
        for (var i = 0; i < websites.length; i++) {
            window.open(websites[i], '_blank');
        }
        document.getElementById('websiteForm').reset();  // 清空表单
    }
    openWebsites(); // 调用函数以打开网页
</script>
