"""
David Liberatore
5/5/2026
This code is for the admin page,
It also has authentication to make sure only admins can go to admin page
"""
from flask_admin import AdminIndexView, expose
from flask import redirect, url_for, flash
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from truckfinder.export import (
    export_foodtrucks_to_csv,
    export_menuitems_to_csv,
    export_hours_to_csv
)

class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for("auth.login"))
        return self.render("admin/index.html")

    @expose('/merge-trucks', methods=['POST'])
    def merge_trucks(self):
        from truckfinder.merge import merge_submitted_trucks
        # Flashes how many were added / skipped on admin page
        try:
            result = merge_submitted_trucks()
            flash(f"Merge complete! {result['added']} added, {result['skipped']} skipped.", "success")
        except Exception as e:
            flash(f"Merge failed: {str(e)}", "error")
        return redirect(url_for('admin.index'))

    """
    David Liberatore
    5/8/2026
    This routes updates the csv file when the admin thinks that it is necessary
    """
    @expose('/update-csv', methods=['POST'])
    def update_csv(self):

        try:
            # Updates each file individually
            export_foodtrucks_to_csv()
            export_menuitems_to_csv()
            export_hours_to_csv()

            flash("CSV files successfully updated!", "success")

        except Exception as e:
            flash(f"CSV update failed: {str(e)}", "error")

        return redirect(url_for('.index'))

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("main.home"))
