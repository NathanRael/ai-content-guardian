import React, { Activity } from "react";

type SectionTitleProps = {
  title: string;
  description?: string;
  icon?: React.ReactNode;
};

const SectionTitle = ({ title, description, icon }: SectionTitleProps) => {
  return (
    <div className="flex-row-start gap-4">
      <div className="size-10 flex-center bg-primary-gradient rounded-lg">
        {icon}
      </div>
      <div>
        <h2 className="text-lead font-semibold">{title}</h2>
        <Activity mode={description ? "visible" : "hidden"}>
          <p>{description}</p>
        </Activity>
      </div>
    </div>
  );
};

export default SectionTitle;
