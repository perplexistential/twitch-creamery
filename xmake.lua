rule("release")
    on_run(function (target)
        import("core.base.semver")

        -- Get the last git tag
        local last_tag = os.iorun("git describe --tags `git rev-list --tags --max-count=1`")

        -- Bump the patch version
        local version = semver.new(last_tag:match("^v(.*)"))
        version:inc("patch")

        -- Create a new git tag and push it
        os.exec("git tag -a v" .. tostring(version) .. " -m \"Release version v" .. tostring(version) .. "\"")
        os.exec("git push origin v" .. tostring(version))
    end)
    set_menu {
        usage = "xmake release",
        description = "create a new release",
        options = {},
    }
