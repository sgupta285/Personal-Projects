import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.CheckBox
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.cs407.connectech.R
import com.cs407.connectech.model.Match

class BestMatchesAdapter(
    private val companies: List<Match>,
    private val onCompanySelected: (Match, Boolean) -> Unit
) : RecyclerView.Adapter<BestMatchesAdapter.ViewHolder>() {

    private val selectedPositions = mutableSetOf<Int>()

    inner class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val companyName: TextView = itemView.findViewById(R.id.companyName)
        val selectButton: CheckBox = itemView.findViewById(R.id.selectButton)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_match, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val company = companies[position]
        holder.companyName.text = company.name
        holder.selectButton.isChecked = selectedPositions.contains(position)

        holder.selectButton.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                selectedPositions.add(position)
            } else {
                selectedPositions.remove(position)
            }
            onCompanySelected(company, isChecked)
        }
    }

    override fun getItemCount() = companies.size
}
